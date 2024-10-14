from datetime import datetime
import pytz

def get_current_date(format: str = None):
    # Definir la zona horaria de Chile
    chile_timezone = pytz.timezone('America/Santiago')
    # Obtener la fecha y hora actual en la zona horaria de Chile
    now_in_chile = datetime.now(chile_timezone)
    
    # Si se proporciona un formato, usarlo; de lo contrario, devolver la fecha por defecto
    if format:
        return now_in_chile.strftime(format)
    else:
        return now_in_chile



