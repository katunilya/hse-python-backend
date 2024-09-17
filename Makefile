test_math_api:
	@curl -i http://localhost:8000/not_found
	@echo
	@echo
	
	@curl -i http://localhost:8000/factorial
	@echo
	@echo
	@curl -i http://localhost:8000/factorial?n=0
	@echo
	@echo
	@curl -i http://localhost:8000/factorial?n=1
	@echo
	@echo
	@curl -i http://localhost:8000/factorial?n=2
	@echo
	@echo
	@curl -i http://localhost:8000/factorial?n=3
	@echo
	@echo
	@curl -i http://localhost:8000/factorial?n=4
	@echo
	@echo
	@curl -i http://localhost:8000/factorial?n=5
	@echo
	@echo
	@curl -i http://localhost:8000/factorial?n=10
	@echo
	@echo
	@curl -i http://localhost:8000/factorial?n=-1
	@echo
	@echo
	
	@curl -i http://localhost:8000/fibonacci
	@echo
	@echo
	@curl -i http://localhost:8000/fibonacci/0
	@echo
	@echo
	@curl -i http://localhost:8000/fibonacci/1
	@echo
	@echo
	@curl -i http://localhost:8000/fibonacci/2
	@echo
	@echo
	@curl -i http://localhost:8000/fibonacci/3
	@echo
	@echo
	@curl -i http://localhost:8000/fibonacci/4
	@echo
	@echo
	@curl -i http://localhost:8000/fibonacci/5
	@echo
	@echo
	@curl -i http://localhost:8000/fibonacci/10
	@echo
	@echo
	@curl -i http://localhost:8000/fibonacci/-1
	@echo
	@echo
	
	@curl -i -X "GET" -H "Accept: application/json" -H "Content-Type: application/json" "http://localhost:8000/mean" -d ''
	@echo
	@echo
	@curl -i -X "GET" -H "Accept: application/json" -H "Content-Type: application/json" "http://localhost:8000/mean" -d '[]'
	@echo
	@echo
	@curl -i -X "GET" -H "Accept: application/json" -H "Content-Type: application/json" "http://localhost:8000/mean" -d '[1,2,3]'
	@echo
	@echo
	@curl -i -X "GET" -H "Accept: application/json" -H "Content-Type: application/json" "http://localhost:8000/mean" -d '[1,2.2,3.3]'
	@echo
	@echo