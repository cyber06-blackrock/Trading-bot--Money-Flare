import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIAnalyst:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key and api_key != "your_google_ai_key_here":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.active = True
        else:
            self.active = False

    def get_market_insight(self, symbol, current_price):
        if not self.active:
            return "AI Analyst is offline. (Invalid API Key)"

        prompt = f"""
        You are a elite crypto trading analyst. 
        Current price of {symbol} is ${current_price}.
        Provide a short, professional trading insight (max 3 sentences). 
        Should the user BUY, SELL, or HOLD? 
        End with a 'Confidence Score' from 1-10.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Analysis failed: {str(e)}"

class CommandParser:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key and api_key != "your_google_ai_key_here":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.active = True
        else:
            self.active = False

    def parse_message(self, message, default_symbol="BTCUSDT"):
        if not self.active:
            # Simple heuristic if AI is offline
            msg = message.lower()
            words = msg.split()
            
            # Default values
            side = "BUY" if any(x in msg for x in ["buy", "long"]) else "SELL" if any(x in msg for x in ["sell", "short"]) else None
            qty = 0.001
            symbol = default_symbol
            
            # Try to find a number for quantity
            for word in words:
                clean_word = word.replace('x', '').replace('X', '')
                try:
                    val = float(clean_word)
                    if 'x' in word.lower():
                        continue # Skip leverage values
                    if val < 10: # Quantities are usually small in BTC
                        qty = val
                        break # Take the first valid quantity found
                except: continue
            
            # Try to find symbol
            for word in words:
                if "btc" in word: symbol = "BTCUSDT"
                elif "eth" in word: symbol = "ETHUSDT"
                elif "sol" in word: symbol = "SOLUSDT"

            if side:
                return {"action": "TRADE", "symbol": symbol, "side": side, "type": "MARKET", "qty": qty, "price": None}
            return {"action": "NONE"}

        prompt = f"""
        Extract trading intent from this message: "{message}"
        Current default symbol is {default_symbol}.
        
        Return ONLY a JSON object with these fields:
        "action": "TRADE", "ANALYZE", or "NONE"
        "symbol": (e.g. "BTCUSDT")
        "side": "BUY" or "SELL"
        "type": "MARKET" or "LIMIT"
        "qty": (number)
        "price": (number or null)

        Example: "Buy 0.01 BTC" -> {{"action": "TRADE", "symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "qty": 0.01, "price": null}}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Find JSON in response
            text = response.text
            start = text.find('{')
            end = text.rfind('}') + 1
            return json.loads(text[start:end])
        except:
            return {"action": "NONE"}
