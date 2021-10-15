import xlwings as xw
import PySimpleGUI as sg
import datetime

#Get the row
def get_collapse_range_string_array():
  sg.popup_ok("Please select the column you want to collapse by")
  column = xw.apps.active.books.active.selection.address
  row = ''
  for char in column:
      if char == ':':
          break
      elif char == '$':
          pass
      else:
          row += str(char)


  sheet = xw.sheets.active
  #Get the last row to avoid going through the whole sheet
  last = sheet.range(row + str(sheet.cells.last_cell.row)).end('up').row
  values = xw.Range(row+str(1)+':'+row+str(last)).value

  #Get an array of arrays of the indices we're going to collapse
  collapse_ranges = []
  checked_indices = []
  for index, value in enumerate(values):
      if index in checked_indices:
          pass
      elif value:
          if index + 1 < len(values):
              if isinstance(values[index], datetime.datetime) and isinstance(values[index+1], datetime.datetime):
                  if values[index].month == values[index+1].month:
                      temp_range = []
                      for i in range(len(values) - (index+1)):
                          if isinstance(values[index+i], datetime.datetime):
                              if values[index].month == values[index+i].month:
                                  temp_range.append(index+i+1)
                                  checked_indices.append(index+i)
                      collapse_ranges.append(temp_range)

  #Change to form of "x:y" for VBA
  temp = []
  for indices in collapse_ranges:
      temp.append(str(indices[0])+':'+str(indices[-1]))
  collapse_ranges = temp

  return collapse_ranges
