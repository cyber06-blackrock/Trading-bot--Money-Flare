def validate_order_params(symbol, side, order_type, quantity, price=None):
    errors = []
    
    if not symbol or not isinstance(symbol, str):
        errors.append("Symbol must be a non-empty string (e.g., BTCUSDT).")
        
    if side.upper() not in ['BUY', 'SELL']:
        errors.append("Side must be either 'BUY' or 'SELL'.")
        
    if order_type.upper() not in ['MARKET', 'LIMIT', 'STOP_LIMIT']:
        errors.append("Order type must be 'MARKET', 'LIMIT', or 'STOP_LIMIT'.")
        
    try:
        qty = float(quantity)
        if qty <= 0:
            errors.append("Quantity must be greater than zero.")
    except (ValueError, TypeError):
        errors.append("Quantity must be a valid number.")
        
    if order_type.upper() in ['LIMIT', 'STOP_LIMIT']:
        if price is None:
            errors.append(f"Price is required for {order_type} orders.")
        else:
            try:
                p = float(price)
                if p <= 0:
                    errors.append("Price must be greater than zero.")
            except (ValueError, TypeError):
                errors.append("Price must be a valid number.")
                
    return errors
