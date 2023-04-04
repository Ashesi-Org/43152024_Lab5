import json
import functions_framework
from flask import Flask, request, jsonify

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


firebase_admin.initialize_app()
db = firestore.client()


@functions_framework.http
def hello_http(request):
    if request.method == 'POST' and request.path == '/voter':
        return(create_record())

    elif request.method == 'POST' and request.path == '/election':
        return(create_election())

    elif request.method == 'GET' and request.path == '/voter':
        voterID = request.args.get("ID")
        return(query_records(voterID)) 

    elif request.method == 'GET' and request.path == '/election':
        electionID = request.args.get("Election_ID")
        return(query_election(electionID)) 
        
    elif request.method == 'DELETE' and "ID" in request.args:
        voterID = request.args.get("ID")
        return delete_record(voterID)

    elif request.method == 'DELETE' and "Election_ID" in request.args:
        return delete_election(request.args.get("Election_ID"))
    
    elif request.method == 'PUT' and "ID" in request.args:
        voterID = request.args.get("ID")
        return update_record(voterID)

    elif request.method == 'PATCH':
        Election_ID,Candidate_ID = request.path.split("/")[-2:]
        return vote(Election_ID,Candidate_ID)


app = Flask(__name__)


#Registering a voter
# @app.route('/voter', methods=['POST'])
def create_record():

    if not request.data:
        return jsonify({"Message": "Request failed"})
    record = json.loads(request.data)
    voter_ref = db.collection("Voters").document(record["ID"])
    voter = voter_ref.get()
    if voter.exists:
        return jsonify({"Error": "The voter with the ID you entered already exists"}), 409
    else:
        db.collection("Voters").document(record["ID"]).set(record)
        return jsonify({"Message":"Voter registered successfully"}), 200


# #Deregistering a voter
# @app.route('/voter/<ID>', methods=['DELETE'])
def delete_record(ID):
    voter_ref = db.collection("Voters").document(ID)
    voter = voter_ref.get()

    if voter.exists:
        db.collection("Voters").document(ID).delete()
        return jsonify({"Message":"Voter deleted successfully"}), 200
    else:
        return jsonify({"Error": "The voter with the ID you entered does not exist"}), 404


# #Retrieving a registered voter
# @app.route('/voter/<ID>', methods=['GET'])
def query_records(ID):
    voter_ref = db.collection("Voters").document(ID)
    voter = voter_ref.get()

    return jsonify (voter.to_dict()), 200


# #Updating a voter's information
# @app.route('/voter/<ID>', methods=['PUT'])
def update_record(ID):
    if not request.data:
        return jsonify({"Message": "Request failed"})

    record = json.loads(request.data)
    voter_ref = db.collection("Voters").document(record["ID"])
    voter = voter_ref.get()

    if voter.exists:
          db.collection("Voters").document(record["ID"]).set(record)
          return jsonify({"Message": "Voter records updated successfully"}), 409
    else:
        return jsonify({"Error":"Voter does not exist"}), 200



#Creating an election
# @app.route('/election', methods=['POST'])
def create_election():
    if not request.data:
        return jsonify({"Message": "Request failed"})
    record = json.loads(request.data)

    election_ref = db.collection("Elections").document(record["Election_ID"])
    election = election_ref.get()
    if election.exists:
        return jsonify({"Error": "The election with the ID you entered already exists"}), 409
    else:
        db.collection("Elections").document(record["Election_ID"]).set(record)
        return jsonify({"Message":"Election created successfully"}), 200


#Deleting an election
# @app.route('/election/<Election_ID>', methods=['DELETE'])
def delete_election(Election_ID):
    election_ref = db.collection("Elections").document(Election_ID)
    election = election_ref.get()

    if election.exists:
        db.collection("Elections").document(Election_ID).delete()
        return jsonify({"Message":"Election deleted successfully"}), 200
    else:
        return jsonify({"Error": "The election with the ID you entered does not exist"}), 409


# #Retrieving an election
# @app.route('/election/<Election_ID>', methods=['GET'])
def query_election(Election_ID):
    election_ref = db.collection("Elections").document(Election_ID)
    election = election_ref.get()

    return jsonify (election.to_dict()), 200


# #Voting in an election
# @app.route('/election/<Election_ID>/<Candidate_ID>', methods=['PATCH'])
def vote(Election_ID,Candidate_ID):
    election_ref = db.collection("Elections").document(Election_ID)
    election = election_ref.get()

    candidate_ref = db.collection("Elections").document(Candidate_ID)
    candidate = candidate_ref.get()

    if not election.exists:
            return jsonify({"error": "election does not exist"}), 404

    Candidates = election.to_dict().get("Candidates")
    if not Candidates:
            return jsonify({"error": "no candidates found for the election"}), 404
        
    for c in Candidates:
        print(c)
        if Candidate_ID == c['Candidate_ID']:
            print(c['Vote_Count'])
            votes = c['Vote_Count'] + 1
            c['Vote_Count'] = votes

            election_ref.update({'Candidates': Candidates})
            return jsonify({"Message": "Vote for candidate {} in election {} has been counted.".format(Candidate_ID, Election_ID)}), 200
                
        else:
            return jsonify({"error": "candidate does not exist"}), 404
        

if __name__ == "__main__":
    app.run()
