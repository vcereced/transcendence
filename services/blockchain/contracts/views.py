from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from web3 import Web3
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

sepolia_node_url = "https://sepolia.infura.io/v3/e9bce358a6aa4324bc1f53e803b54662"

web3 = Web3(Web3.HTTPProvider(sepolia_node_url))


contract_abi = None
try:
    abi_file_path = "./contracts/TournamentRegistry.json"
    with open(abi_file_path, 'r') as f:
        contract_abi = json.load(f)
except FileNotFoundError:
    contract_abi = None
except json.JSONDecodeError:
    contract_abi = None

contract_address = os.getenv("CONTRACT_ADDRESS")

private_key = os.getenv("SEPOLIA_PRIVATE_KEY")
if not private_key:
    logger.error("Advertencia: La clave privada de Sepolia no se ha configurado como variable de entorno.")


contract = None
if contract_abi and web3.is_connected() and contract_address:
    try:
        contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    except Exception as e:
        logger.error(f"Error al inicializar el contrato: {e}")
else:
    logger.error("No se pudo inicializar el contrato debido a problemas con web3:", web3.is_connected(), ", ABI:", contract_abi is not None, ", dirección:", contract_address is not None)

@csrf_exempt
def register_tournament_api(request):

    if request.method == 'POST':
        if not contract:
            logger.error("Error: No se pudo inicializar el contrato dentro de la vista!!.")
            return JsonResponse({'error': 'No se pudo inicializar el contratowwe'}, status=500)
        if not web3.is_connected():
            logger.error("Error: No se está conectado a la red Sepolia dentro de la vista!!.")
            return JsonResponse({'error': 'No se está conectado a la red Sepolia'}, status=500)
        if not private_key:
            logger.error("Error: Clave privada no configurada dentro de la vista!!.")
            return JsonResponse({'error': 'Clave privada no configurada'}, status=500)

        try:
            data = json.loads(request.body)
            tournament_id = data.get('id')
            tournament_name = data.get('name')
            winner = data.get('winner')
            tree_hash = data.get('treeHash')

            if not all([tournament_id, tournament_name, winner, tree_hash]):
                return JsonResponse({'error': 'Faltan datos en la solicitud'}, status=400)

            account = web3.eth.account.from_key(private_key)
            nonce = web3.eth.get_transaction_count(account.address)
            transaction = contract.functions.registerTournament(
                tournament_id,
                tournament_name,
                winner,
                tree_hash
            ).build_transaction({
                'gas': 600000,  
                'gasPrice': web3.eth.gas_price,
                'nonce': nonce,
            })

            signed_transaction = account.sign_transaction(transaction)

            transaction_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)

            return JsonResponse({'status': 'success', 'transaction_hash': transaction_hash.hex()})

        except json.JSONDecodeError:
            logger.error("Error: Datos JSON inválidos en la solicitud.")
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            logger.error(f"Error al registrar el torneo dentro de la vista: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        logger.error("Error: Método no permitido para /register.")
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    

def get_tournament_details(request, tournament_id):
    try:
        tournament = contract.functions.getTournament(tournament_id).call()

        tournament_data = {
            'id': tournament[0],
            'name': tournament[1],
            'winner': tournament[2],
            'treeHash': tournament[3],
            'registeredAt': tournament[4],
        }
        return JsonResponse(tournament_data)
    except Exception as e:
        logger.error(f"Error al obtener los detalles del torneo {tournament_id}: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
def get_tournaments_ids(request):
    try:

        ids = contract.functions.getAllTournamentIds().call()
        return JsonResponse({'tournament_ids': ids})
    except Exception as e:
        logger.error(f"Error al obtener los IDs de los torneos: {e}")
        return JsonResponse({'error': str(e)}, status=500)