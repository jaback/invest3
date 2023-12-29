from enum import Enum
from os import listdir
from os.path import isfile, join
from PyPDF2 import PdfReader
from datetime import datetime


class NegotiationNotesFields(Enum):
    trading_date = 'Data Pregão'
    id = 'CPF'
    debentures = 'Debêntures'
    sales = 'Vendas à vista'
    purchases = 'Compras à vista'
    net_value = 'Valor Líquido das Operações'
    settlement_fee = 'Taxa de Liquidação'
    registration_fee = 'Taxa de Registro'
    fees = 'Emolumentos'
    operations = "Valor das Operações"
    tickets = []
    file = ''

class NegotiationNotesTickets(Enum):
    market = 'BOVESPA'
    ticket = 'ticket'
    type = 'type'
    amount = 'amount'
    price = 'price'
    value = 'value'


def get_trading_date(element):
    return element[NegotiationNotesFields.trading_date.name]

def to_float(element):
    return float(element.replace('.', '').replace(',', '.'))
    
def load_negotiation_notes(path):
    coll_negotiation_note = []
    
    for file_name in [f for f in listdir(path) if isfile(join(path, f))]:
        with open(path / file_name, 'rb') as f:
            text_list = []

            # extract_pdf
            reader = PdfReader(f)
            for i in range(len(reader.pages)):
                text = reader.pages[i].extract_text()
                text_list.extend(text.splitlines())

            # filter_negotiation_note
            negotiation_note = {}
            tickets = []
            
            negotiation_note[NegotiationNotesFields.file.name] = file_name
            for i in range(len(text_list)):
                word = text_list[i]
                if word == NegotiationNotesFields.id.value:
                    negotiation_note[NegotiationNotesFields.id.name] = text_list[i + 1]
                elif word == NegotiationNotesFields.trading_date.value:
                    negotiation_note[NegotiationNotesFields.trading_date.name] = datetime.strptime(text_list[i + 1], '%d/%m/%Y').date()
                elif word == NegotiationNotesFields.debentures.value:
                    negotiation_note[NegotiationNotesFields.debentures.name] = to_float(text_list[i + 1])
                elif word == NegotiationNotesFields.sales.value:
                    negotiation_note[NegotiationNotesFields.sales.name] = to_float(text_list[i + 1])
                elif word == NegotiationNotesFields.purchases.value:
                    negotiation_note[NegotiationNotesFields.purchases.name] = to_float(text_list[i + 1])
                elif word == NegotiationNotesFields.net_value.value:
                    negotiation_note[NegotiationNotesFields.net_value.name] = to_float(text_list[i + 1])
                elif word == NegotiationNotesFields.settlement_fee.value:
                    negotiation_note[NegotiationNotesFields.settlement_fee.name] = to_float(text_list[i + 1])
                elif word == NegotiationNotesFields.registration_fee.value:
                    negotiation_note[NegotiationNotesFields.registration_fee.name] = to_float(text_list[i + 1])
                elif word == NegotiationNotesFields.fees.value:
                    negotiation_note[NegotiationNotesFields.fees.name] = to_float(text_list[i + 1])
                elif word == NegotiationNotesFields.operations.value:
                    negotiation_note[NegotiationNotesFields.operations.name] = to_float(text_list[i + 2])
                elif word == NegotiationNotesTickets.market.value:
                    ticket = {}
                    ticket_name = text_list[i + 3].split()[0]
                    ticket[NegotiationNotesTickets.ticket.name] = ticket_name[:-1] if ticket_name.endswith("F") else ticket_name
                    ticket[NegotiationNotesTickets.type.name] = text_list[i + 1]
                    amount = 0
                    index = i + 4
                    try:
                        amount = int(text_list[index])
                    except:
                        try:
                            index += 1
                            amount = int(text_list[index])
                        except:
                            try:
                                index += 1
                                amount = int(text_list[index])
                            except:
                                index += 1
                                amount = int(text_list[index])    
                    ticket[NegotiationNotesTickets.amount.name] = amount
                    index += 1
                    ticket[NegotiationNotesTickets.price.name] = to_float(text_list[index])
                    index += 1
                    ticket[NegotiationNotesTickets.value.name] = to_float(text_list[index])
                    tickets.append(ticket)
                    
            negotiation_note[NegotiationNotesFields.tickets.name] = tickets
            coll_negotiation_note.append(negotiation_note)

    coll_negotiation_note.sort(key=get_trading_date)
    return coll_negotiation_note
