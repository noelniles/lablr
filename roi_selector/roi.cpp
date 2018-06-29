#include "roi.h"
#include "ui_roi.h"

ROI::ROI(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::ROI)
{
    ui->setupUi(this);
}

ROI::~ROI()
{
    delete ui;
}
