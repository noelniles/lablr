#include "roi.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    ROI w;
    w.show();

    return a.exec();
}
