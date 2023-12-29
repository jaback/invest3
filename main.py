import datetime
import platform
import csv 
from pathlib import Path
from negotiation_notes import to_float, load_negotiation_notes, NegotiationNotesFields, NegotiationNotesTickets


os = platform.system()
year = datetime.date.today().year
input_path = Path(f'{Path.home()}/Documents/NuInvest/{year}') if os == "Linux" else Path(f'{Path.home()}\\Documents\\NuInvest\\{year}')
    
index_ticket = 0
index_type = 1
index_amount = 2
index_cost = 11
index_average = 12
index_desc = 13


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
            line.append(i[NegotiationNotesFields.file.name])

            rows.append(line)


def read_start_position(rows):
    with open(f'{input_path}p0.csv', 'r') as f:
        for row in csv.reader(f):
            try:
                extra = [''] * (index_desc + 1)
                extra[index_ticket] = row[0]
                extra[index_type] = 'C'
                extra[index_amount] = int(row[1])
                extra[index_cost] = round(to_float(row[2]), 2)
                extra[index_average] = round(to_float(row[2]) / int(row[1]), 2)
                extra[index_desc] = f'{year}p0.csv'

                rows.insert(0, extra)
            except:
                pass


def sum_tickets(rows, group_rows):
    last_ticket = rows[0][index_ticket]
    sum_amount = 0
    sum_cost = 0

    for i in rows:
        is_C = i[index_type] == 'C'

        if (last_ticket != i[index_ticket]):
            add_extra_line(group_rows, last_ticket, sum_amount, sum_cost, True)
            sum_amount = i[index_amount] if is_C else (i[index_amount] * -1)
            sum_cost = i[index_cost] if is_C else (i[index_cost] * -1)
            group_rows.append(i)
        else:
            if not is_C:
                group_rows.append(i)
                average_last = sum_cost / sum_amount
                average_V = i[index_cost] / i[index_amount]
                average_diff = average_V - average_last
                sum_amount -= i[index_amount]
                sum_cost -= i[index_cost]
                add_extra_line(group_rows, last_ticket, sum_amount, (average_diff * i[index_amount]), False)
            else:
                sum_amount += i[index_amount]    
                sum_cost += i[index_cost]
                group_rows.append(i)
            
        last_ticket = i[index_ticket]

    add_extra_line(group_rows, last_ticket, sum_amount, sum_cost, True)


def add_extra_line(group_rows, last_ticket, sum_amount, sum_cost, is_resume):
    extra = [''] * (index_desc + 1)
    extra[index_ticket] = last_ticket
    extra[index_amount] = sum_amount
    if is_resume:
        extra[index_cost] = round(sum_cost, 2) if sum_amount > 0 else 0
        extra[index_average] = round(sum_cost / sum_amount, 2) if (sum_amount > 0) else None
        extra[index_desc] = '*** RESUME ***' 
    else:
        extra[index_cost] = round(sum_cost, 2)
        extra[index_desc] = 'partial' 
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
        'average',
        'description']
    
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