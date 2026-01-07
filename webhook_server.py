from flask import Flask, request, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)
SPARQL_ENDPOINT = "https://jena-fuseki-4hhh.onrender.com/books/sparql"  # ← замените на ваш Fuseki URL

GENRE_MAP = {
    "Фантастика": "http://www.semanticweb.org/vecni/ontologies/2026/0/book-recommender-ontology#Fantasy",
    "Научная фантастика": "http://www.semanticweb.org/vecni/ontologies/2026/0/book-recommender-ontology#ScienceFiction",
    "Детектив": "http://www.semanticweb.org/vecni/ontologies/2026/0/book-recommender-ontology#Mystery",
    "Наука": "http://www.semanticweb.org/vecni/ontologies/2026/0/book-recommender-ontology#Science"
}

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    slots = data.get("slots", {})
    genre_ru = slots.get("genre", "Научная фантастика")
    genre_iri = GENRE_MAP.get(genre_ru, GENRE_MAP["Научная фантастика"])

    query = f"""
    PREFIX : <http://www.semanticweb.org/vecni/ontologies/2026/0/book-recommender-ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?title WHERE {{
      ?book a :Book ;
            :title ?title ;
            :hasGenre ?g .
      ?g a <{genre_iri}> .   # ← ищем индивиды типа :ScienceFiction, а не IRI класса
    }} LIMIT 3
    """
    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        titles = [r["title"]["value"] for r in results["results"]["bindings"]]
        text = f"Вот что можно почитать в жанре «{genre_ru}»: {', '.join(titles)}." if titles else \
               f"К сожалению, книг в жанре «{genre_ru}» пока нет."
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"text": f"Ошибка: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)