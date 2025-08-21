"""This module provides tools for payment validation and processing.

These tools simulate the payment validation workflow including bank validation,
receipt verification, order validation, and payment search functionality.
"""

import random
from typing import Any, Callable, List


async def auth_user_tool(user_email: str, user_cedula: str) -> dict[str, Any]:
    """Autenticar usuario usando su email y número de cédula.

    Esta función verifica las credenciales del usuario y devuelve información sobre su estado de autenticación.
    """
    # Simulate random authentication success/failure
    if random.choice([True, False, True]):  # 66% success rate
        return {
            "success": True,
            "user_email": user_email,
            "user_cedula": user_cedula,
            "is_authenticated": True,
            "message": f"Usuario {user_email} autenticado exitosamente",
        }
    return {
        "success": False,
        "error": "Credenciales inválidas",
        "message": "No se pudo autenticar al usuario. Verifica el email y cédula.",
    }


async def validate_receipt_tool(receipt_image: str) -> dict[str, Any]:
    """Validar comprobante de pago desde imagen.

    Args:
        receipt_image: Imagen del comprobante en formato base64 o URL
    """
    # Simulate receipt validation (check if image is provided)
    if not receipt_image or len(receipt_image) < 10:
        return {
            "success": False,
            "error": "Imagen requerida",
            "message": "Debes proporcionar una imagen del comprobante de pago",
        }

    validation_success = random.choice([True, False, True])  # 66% success rate

    if validation_success:
        return {
            "success": True,
            "payment_receipt_validated": True,
            "message": "Comprobante de pago válido y legible",
        }
    else:
        return {
            "success": False,
            "error": "Comprobante inválido",
            "message": "El comprobante no es válido. Asegúrate de que sea una imagen clara y oficial.",
        }


async def extract_payment_data_tool(receipt_image: str) -> dict[str, Any]:
    """Extraer datos del comprobante de pago.

    Args:
        receipt_image: Imagen del comprobante en formato base64 o URL
    """
    # Check if image is provided
    if not receipt_image or len(receipt_image) < 10:
        return {
            "success": False,
            "error": "Imagen requerida",
            "message": "Debes proporcionar una imagen del comprobante de pago",
        }

    # Simulate data extraction
    extraction_success = random.choice([True, False, True, True])  # 75% success rate

    if extraction_success:
        # Generate fake payment data
        fake_amounts = [150.50, 250.00, 89.99, 500.25, 75.80]
        fake_references = [
            "REF001234",
            "PAY567890",
            "TRX999888",
            "BNK445566",
            "MOV112233",
        ]
        fake_dates = [
            "2025-01-15",
            "2025-01-14",
            "2025-01-13",
            "2025-01-16",
            "2025-01-12",
        ]

        return {
            "success": True,
            "payment_amount": random.choice(fake_amounts),
            "payment_reference": random.choice(fake_references),
            "payment_date": random.choice(fake_dates),
            "message": "Datos extraídos exitosamente del comprobante",
        }
    else:
        return {
            "success": False,
            "error": "Error en extracción",
            "message": "No se pudieron extraer los datos del comprobante. Verifica que la imagen sea clara.",
        }


async def validate_bank_tool(bank_name: str) -> dict[str, Any]:
    """Validar banco de destino del pago.

    Args:
        bank_name: Nombre del banco donde se realizó el pago
    """
    valid_banks = [
        "Banesco",
        "Mercantil",
        "Venezuela",
        "Bicentenario",
        "Provincial",
        "Exterior",
    ]

    if bank_name.title() in valid_banks:
        return {
            "success": True,
            "bank_validated": True,
            "payment_bank": bank_name.title(),
            "message": f"Banco {bank_name.title()} validado correctamente",
        }
    else:
        return {
            "success": False,
            "error": "Banco no válido",
            "message": f"El banco '{bank_name}' no está en nuestra lista de bancos válidos. Bancos válidos: {', '.join(valid_banks)}",
        }


async def validate_order_tool(order_number: str) -> dict[str, Any]:
    """Validar número de orden asociada al pago.

    Args:
        order_number: Número de orden a validar
    """
    # Simulate order validation
    order_exists = random.choice([True, False, True, True])  # 75% success rate

    if order_exists and len(order_number) >= 6:
        return {
            "success": True,
            "order_validated": True,
            "payment_order": order_number,
            "message": f"Orden {order_number} encontrada y validada",
        }
    else:
        return {
            "success": False,
            "error": "Orden no encontrada",
            "message": f"La orden '{order_number}' no existe o no es válida. Verifica el número de orden.",
        }


async def search_payment_tool(
    payment_reference: str, payment_amount: float, payment_date: str
) -> dict[str, Any]:
    """Buscar pago en el sistema usando los datos del comprobante.

    Args:
        payment_reference: Referencia del pago
        payment_amount: Monto del pago
        payment_date: Fecha del pago
    """
    # Simulate payment search
    payment_found = random.choice([True, False, True])  # 66% success rate

    if payment_found:
        statuses = ["Procesado", "En verificación", "Pendiente", "Completado"]
        status = random.choice(statuses)

        return {
            "success": True,
            "payment_found": True,
            "payment_status": status,
            "message": f"Pago encontrado. Estado: {status}. Referencia: {payment_reference}, Monto: ${payment_amount}, Fecha: {payment_date}",
        }
    else:
        return {
            "success": False,
            "error": "Pago no encontrado",
            "message": f"No se encontró ningún pago con la referencia {payment_reference} por el monto ${payment_amount} en la fecha {payment_date}",
        }


TOOLS: List[Callable[..., Any]] = [
    auth_user_tool,
    validate_receipt_tool,
    extract_payment_data_tool,
    validate_bank_tool,
    validate_order_tool,
    search_payment_tool,
]
