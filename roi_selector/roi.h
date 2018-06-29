#ifndef ROI_H
#define ROI_H

#include <QMainWindow>

namespace Ui {
class ROI;
}

class ROI : public QMainWindow
{
    Q_OBJECT

public:
    explicit ROI(QWidget *parent = 0);
    ~ROI();

private:
    Ui::ROI *ui;
};

#endif // ROI_H
