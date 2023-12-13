import datetime
import platform
import pprint
from pathlib import Path
from negotiation_notes import load_negotiation_notes, NegotiationNotesFields, NegotiationNotesTickets


os = platform.system()
year = datetime.date.today().year
input_path = Path(f'{Path.home()}/Documents/NuInvest/{year}') if os == "Linux" else Path(f'{Path.home()}\\Documents\\NuInvest\\{year}')
    
if __name__ == '__main__':

    coll_negotiation_notes = load_negotiation_notes(input_path)

    print(f'\n[{input_path}]\nTotals:\n')
    print(f'coll_negotiation_notes: {len(coll_negotiation_notes)}\n')

    grouped = []
    for i in coll_negotiation_notes:
        print(f'{i[NegotiationNotesFields.trading_date.name]}', end = " ")
                    
        total_fees = i[NegotiationNotesFields.settlement_fee.name] + i[NegotiationNotesFields.fees.name]
        amount = i[NegotiationNotesFields.amount.name]
        for j in i[NegotiationNotesFields.tickets.name]:
            ticket = j[NegotiationNotesTickets.ticket.name]
            type = j[NegotiationNotesTickets.type.name]
            #print(f'{ticket}({type})', end = " ")
            
            grouped.append(f'{ticket};{type}')
            if type == 'C':
                print('compra')
            elif type == 'V':
                print('venda')
        print(amount)
        
    print()
    pprint.pprint(grouped)
    
    print()
