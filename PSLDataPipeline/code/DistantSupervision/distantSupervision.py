import json

def loadTargetTypes(filename):
  map = {}
  with open(filename, 'r') as fin:
    for line in fin:
      seg = line.strip('\r\n').split('\t')
      fbType = seg[0]
      cleanType = seg[1]
      map[fbType] = cleanType
  return map

def linkToFB(jsonFname, outFname, entityTypesFname, relationTypesFname, freebase_dir):
  mid2typeFname = freebase_dir+'/freebase-mid-type.map'
  mid2nameFname = freebase_dir+'/freebase-mid-name.map'
  relationTupleFname = freebase_dir+'/freebase-facts.txt'

  mid2typeFname_out = freebase_dir+'/freebase-mid-type_out.map'
  mid2nameFname_out = freebase_dir+'/freebase-mid-name_out.map'
  relationTupleFname_out = freebase_dir+'/freebase-facts_out.txt'

  mid2types = {}
  name2mids = {}
  mids2relation = {}
  targetEMTypes = loadTargetTypes(entityTypesFname)#{'<http://rdf.freebase.com/ns/people.person>':'PERSON', '<http://rdf.freebase.com/ns/organization.organization>':'ORGANIZATION', '<http://rdf.freebase.com/ns/location.location>':'LOCATION'}
  with open(mid2typeFname_out, 'r') as mid2typeFile, open(mid2nameFname_out, 'r') as mid2nameFile, open(relationTupleFname_out, 'r') as relationTupleFile:
  #open(mid2typeFname_out, 'w') as mid2typeFile_out, open(mid2nameFname_out, 'w') as mid2nameFile_out, open(relationTupleFname_out, 'w') as relationTupleFile_out:
    for line in mid2typeFile:
      seg = line.strip('\r\n').split('\t')
      mid = seg[0]
      type = seg[1].split('/')[-1][:-1]       
      if type in targetEMTypes:
        #mid2typeFile_out.write(line)
        if mid in mid2types:
          mid2types[mid].add(targetEMTypes[type])
        else:
          mid2types[mid] = set([targetEMTypes[type]])
    print('finish loading mid2typeFile',len(mid2types))

    targetRMTypes = loadTargetTypes(relationTypesFname)
    for line in relationTupleFile:
      seg = line.strip('\r\n').split('\t')
      mid1 = seg[0]
      type = seg[1].split('/')[-1][:-1]
      mid2 = seg[2]
      if type in targetRMTypes and mid1 in mid2types and mid2 in mid2types:
        #relationTupleFile_out.write(line)
        key = (mid1, mid2)
        if key in mids2relation:
          mids2relation[key].add(targetRMTypes[type])  #add(type) 
        else:
          mids2relation[key] = set([targetRMTypes[type]])  #set([type]) 
    print('finish loading relationTupleFile',len(mids2relation))

    for line in mid2nameFile:
      seg = line.strip('\r\n').split('\t')
      mid = seg[0]
      name = seg[1].lower()
      if mid in mid2types and name.endswith('@en'):
        name = name[1:].replace('"@en', '')
        #mid2nameFile_out.write(line)
        if name in name2mids:
          name2mids[name].add(mid)
        else:
          name2mids[name] = set([mid])
    print('finish loading mid2nameFile',len(name2mids))
  return mid2types,mids2relation,name2mids

def linkJson2Freebase(jsonFname, outFname,mid2types, mids2relation, name2mids):
  with open(jsonFname, 'r') as fin, open(outFname, 'w') as fout:
    linkableCt = 0
    for line in fin:
      sentDic = json.loads(line.strip('\r\n'))
      entityMentions = []
      for em in sentDic['entityMentions']:
        emText = em['text'].lower()
        types = set()
        if emText in name2mids:
          linkableCt += 1
          mids = name2mids[emText]
          for mid in mids:
            types.update(set(mid2types[mid]))
          if em['label']=='None':
            em['label'] = ','.join(types)
        else:
          entityMentions.append(em)
        if len(types) > 0:
          entityMentions.append(em)
      sentDic['entityMentions'] = entityMentions

      relationMentions = []
      for rm in sentDic['relationMentions']:
        e1text=rm['em1Text'].lower()
        e2text=rm['em2Text'].lower()
        rm['true_label']=rm['label']
        rm['label']='None'
        labels=set()
        if e1text in name2mids and e2text in name2mids:
          for mid1 in name2mids[e1text]:
            for mid2 in name2mids[e2text]:
              if (mid1, mid2) in mids2relation:
                #print e1text,e2text, mids2relation[(mid1, mid2)]
                labels.update(set(mids2relation[(mid1, mid2)]))
        if len(labels) > 0:
          rm['label'] = ','.join(labels)
        relationMentions.append(rm)
        sentDic['relationMentions']=relationMentions
      fout.write(json.dumps(sentDic) + '\n')