#!/usr/bin/python
#coding:utf-8

import couchdb

couch = couchdb.Server("http://couchadmin:adminpwd@127.0.0.1:5984/")

def LoginCouchdb():
    if couch["baas"]:
        return couch["baas"]
    else:
        couch.create("baas")
        return couch["baas"]

selector ={
   "selector": {
      "_id": {
         "$gt": None
      }
   },
  "fields": ["_id", "_rev", "domain", "consensus", "orders", "orgs"]
}

def QueryList(db):
    for row in db.find(selector):
        print(row.__dict__)
        if "_id" in row:
            print(row["_id"])
        if "domain" in row:
            print(row["domain"])


def QueryById(db,id):
    selectorById = {
        "selector": {
            "_id": id
        },
        "fields": ["_id", "_rev", "domain", "apiip","consensus", "orders", "orgs","ordername","orderid","channel"]
    }
    doc = {}
    for row in db.find(selectorById):
        doc = row
    return doc