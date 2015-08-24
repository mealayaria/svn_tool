# coding=utf-8

import xlrd


class xl_rd:
    def __init__(self, src_excel):
        self.src_xls = xlrd.open_workbook(src_excel)   
        self.table = self.src_xls.sheets()[0]
        self.nrows = self.table.nrows

    def get_commit_info(self, ):
        return map(lambda row: self.table.row_values(row), range(1, self.nrows))
            
            
#def xl_wt(des_xl, table_list):
#    wt_xl = xlwt.Workbook()
#    wt_sht = wt_xl.add_sheet('sheet 1')
#    rows = len(table_list)
#    cols = 3
#    for row in range(rows):
#        for col in range(cols):
#            wt_sht.write(row, col, table_list[row][col])
#    wt_xl.save(des_xl)

if __name__ == '__main__':
    src_xls = xl_rd('test1.xlsx')
    src_xls.get_commit_info()
