from datetime import datetime

def calculate_time_difference(start_date: datetime, end_date: datetime):
    if start_date and end_date:
        # Convertir ambos datetime a naive (sin información de zona horaria)
        start_date = start_date.replace(tzinfo=None)
        end_date = end_date.replace(tzinfo=None)

        # Calcular la diferencia de tiempo
        time_difference = end_date - start_date

        # Obtener la diferencia en horas
        difference_in_hours = time_difference.total_seconds() / 3600

        # Redondear a un decimal y devolver 0 si es menor a 0
        return round(difference_in_hours, 1) if difference_in_hours > 0 else 0
    else:
        return None

