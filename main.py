import datetime
import platform
import csv 
from pathlib import Path
from negotiation_notes import to_float, load_negotiation_notes, NegotiationNotesFields, NegotiationNotesTickets


os = platform.system()
year = datetime.date.today().year
input_path = Path(f'{Path.home()}/Documents/NuInvest/{year}') if os == "Linux" else Path(f'{Path.home()}\\Documents\\NuInvest\\{year}')
    

def extract_rows(coll_negotiation_notes, rows):
    for i in coll_negotiation_notes:
        total_fees = i[NegotiationNotesFields.settlement_fee.name] + i[NegotiationNotesFields.fees.name]
        fee1 = abs(i[NegotiationNotesFields.settlement_fee.name])
        fee2 = abs(i[NegotiationNotesFields.fees.name])
        operations = i[NegotiationNotesFields.operations.name]

        total_fees = fee1 + fee2

        for j in i[NegotiationNotesFields.tickets.name]:
            ticket = j[NegotiationNotesTickets.ticket.name]
            type = j[NegotiationNotesTickets.type.name]    
            value = j[NegotiationNotesTickets.value.name]
            amount = j[NegotiationNotesTickets.amount.name]

            nc = value / operations
            proportional = total_fees * nc
            cost = (value + proportional) if type == 'C' else (value - proportional)
            average = cost / amount
            
            line = [] 
            line.append(ticket)
            line.append(type)
            line.append(amount)
            line.append(i[NegotiationNotesFields.trading_date.name].strftime("%d/%m/%Y"))
            line.append(value)
            line.append(fee1)
            line.append(fee2)
            line.append(total_fees)
            line.append(operations)
            line.append(round(nc, 2))
            line.append(round(proportional, 2))
            line.append(round(cost, 2))
            line.append(round(average, 2))

            rows.append(line)


def read_start_position(rows):
    with open(f'{input_path}p0.csv', 'r') as f:
        for row in csv.reader(f):
            try:
                index_ticket = 0
                index_type = 1
                index_amount = 2
                index_cost = 11

                extra = [''] * (index_cost + 1)
                extra[index_ticket] = row[0]
                extra[index_type] = 'C'
                extra[index_amount] = int(row[1])
                extra[index_cost] = round(to_float(row[2]), 2)

                rows.insert(0, extra)
            except:
                pass


def sum_tickets(rows, group_rows):
    index_ticket = 0
    index_type = 1
    index_amount = 2
    index_cost = 11

    last_ticket = rows[0][index_ticket]
    sum_amount = 0
    sum_cost = 0

    for i in rows:
        if (last_ticket != i[index_ticket]):
            add_extra_line(group_rows, index_ticket, index_amount, index_cost, last_ticket, sum_amount, sum_cost)
            sum_amount = i[index_amount] if i[index_type] == 'C' else (i[index_amount] * -1)
            sum_cost = i[index_cost] if i[index_type] == 'C' else (i[index_cost] * -1)
        else:
            sum_amount = (sum_amount + i[index_amount]) if i[index_type] == 'C' else (sum_amount - i[index_amount])
            sum_cost = (sum_cost + i[index_cost]) if i[index_type] == 'C' else (sum_cost - i[index_cost])
            
        last_ticket = i[index_ticket]
        group_rows.append(i)

    add_extra_line(group_rows, index_ticket, index_amount, index_cost, last_ticket, sum_amount, sum_cost)


def add_extra_line(group_rows, index_ticket, index_amount, index_cost, last_ticket, sum_amount, sum_cost):
    extra = [''] * (index_cost + 1)
    extra[index_ticket] = last_ticket
    extra[index_amount] = sum_amount
    extra[index_cost] = round(sum_cost, 2) if sum_amount > 0 else 0
    group_rows.append(extra)


def write_output(fields, group_rows):
    with open(f'{input_path}.csv', 'w') as f:
        write = csv.writer(f)

        write.writerow(fields)
        write.writerows(group_rows)


if __name__ == '__main__':
    print(f'\n[{input_path}]\nTotals:')

    coll_negotiation_notes = load_negotiation_notes(input_path)
    print(f'coll_negotiation_notes: {len(coll_negotiation_notes)}')

    fields = [
        NegotiationNotesTickets.ticket.name, 
        NegotiationNotesTickets.type.name, 
        NegotiationNotesTickets.amount.name, 
        NegotiationNotesFields.trading_date.name, 
        NegotiationNotesTickets.value.name, 
        NegotiationNotesFields.settlement_fee.name, 
        NegotiationNotesFields.fees.name, 
        'total_fees', 
        NegotiationNotesFields.operations.name, 
        'NC', 
        'proportional', 
        'cost',
        'average']
    
    rows = []
    extract_rows(coll_negotiation_notes, rows)
    read_start_position(rows)
    rows.sort(key=lambda x: x[0])
    print(f'rows: {len(rows)}')

    group_rows = []
    sum_tickets(rows, group_rows)
    print(f'group_rows: {len(group_rows)}')

    write_output(fields, group_rows)
    print(f'output: {input_path}.csv')