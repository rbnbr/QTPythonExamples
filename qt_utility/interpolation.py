from PySide6.QtGui import QColor


def interpolate_colors(q1: QColor, q2: QColor, t: float, method="linear") -> QColor:
    if method == "linear":
        ri = q1.redF() * t + (t-1) * q2.redF()
        gi = q1.greenF() * t + (t - 1) * q2.greenF()
        bi = q1.blueF() * t + (t - 1) * q2.blueF()
        ai = q1.alphaF() * t + (t - 1) * q2.alphaF()

        qi = QColor()
        qi.setRedF(ri)
        qi.setGreenF(gi)
        qi.setBlueF(bi)
        qi.setAlphaF(ai)

        return qi
    else:
        raise NotImplementedError()
