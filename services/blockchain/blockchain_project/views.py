import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.conf import settings
from web3 import Web3
from django.core.cache import cache
from django.utils.decorators import method_decorator



@csrf_exempt
def register_tournament_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tournament_id = data.get('id')
            tournament_name = data.get('name')
            winner = data.get('winner')
            tree_hash = data.get('treeHash')

            # Validar que todos los campos necesarios estén presentes
            if not all([tournament_id, tournament_name, winner, tree_hash]):
                return JsonResponse({'error': 'Faltan datos en la solicitud'}, status=400)

            # Aquí iría la lógica para interactuar con el smart contract
            # (lo implementaremos en el siguiente paso)
            transaction_hash = "PROVISIONAL_HASH" # Placeholder

            return JsonResponse({'status': 'success', 'transaction_hash': transaction_hash})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)