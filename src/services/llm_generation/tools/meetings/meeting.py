def set_meeting(nom, jour) -> str:
    """
    Permet de fixer ou d'enregistres les rendez-vous dans l'agenda.

    Args:
        nom (str): nom de la personne avec qui j'ai rendez-vous.
        jour (str): jour du rendez-vous.

    Returns:
        str: fixe le rendez-vous et retourne une confirmation.
    """
    confirmation = f"un rendez-vous a bien été fixé avec {nom} le {jour}"
    return confirmation