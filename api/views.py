from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def test_response(request):
	response = {
		'Packages': 'package1'
	}
	return Response(response)