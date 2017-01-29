def hms_to_s(hms: str) -> int:
    """
    Convert hh:mm:ss to sum of seconds
    :param hms:
    :return:
    """
    l = list(map(int, hms.split(':')))
    return sum(n * sec for n, sec in zip(l[::-1], (1, 60, 3600)))
