def merge_phrases(doc):
    with doc.retokenize() as retokenizer:
        for np in list(doc.noun_chunks):
            tokens_to_merge = [token for token in np if token.dep_ != "amod"]
            
            if tokens_to_merge:
                span = doc[tokens_to_merge[0].i : tokens_to_merge[-1].i + 1]
                attrs = {
                    "tag": span.root.tag_,
                    "lemma": span.root.lemma_,
                    "ent_type": span.root.ent_type_,
                }
                retokenizer.merge(span, attrs=attrs)
    return doc

def get_dependencies_for_noun(doc, noun):
    
    doc = merge_phrases(doc)    
    dependencies = []
    
    for token in doc:
        if (noun in token.text or noun in token.head.text) and (token.pos_ == "NOUN" or token.pos_ == "PROPN") and (token.head.pos_ == "VERB" or token.head.pos_ == "AUX"):
            dependencies.append({
                "head": token.head.text,
                "child": token.text,
                "dep_h": token.head.dep_,
                "pos_h": token.head.pos_,
                "lemma_h": token.head.lemma_,
                "dep_c": token.dep_,
                "pos_c": token.pos_,
                "lemma_c": token.lemma_
            })
        
        if (token.pos_ == "NOUN" or token.pos_ == "PROPN"):
            # Direct Dependencies
            for child in token.children:
                if child.pos_ == "ADJ" and (noun in token.text or noun in child.text):             
                    dependencies.append({
                        "head": token.text,
                        "child": child.text,
                        "dep_h": token.dep_,
                        "pos_h": token.pos_,
                        "lemma_h": token.lemma_,
                        "dep_c": child.dep_,
                        "pos_c": child.pos_,
                        "lemma_c": child.lemma_
                    })
                if (child.pos_ == "NOUN" or child.pos_ == "PROPN") and (noun in token.text or noun in child.text):                    
                    dependencies.append({
                        "head": token.text,
                        "child": child.text,
                        "dep_h": token.dep_,
                        "pos_h": token.pos_,
                        "lemma_h": token.lemma_,
                        "dep_c": child.dep_,
                        "pos_c": child.pos_,
                        "lemma_c": child.lemma_
                    })
            
            # Broader Relations through ancestors
            for ancestor in token.ancestors:
                if ancestor.pos_ == "ADJ" and (noun in token.text or noun in ancestor.text):                          
                    dependencies.append({
                        "head": token.text,
                        "child": ancestor.text,
                        "dep_h": token.dep_,
                        "pos_h": token.pos_,
                        "lemma_h": token.lemma_,
                        "dep_c": ancestor.dep_,
                        "pos_c": ancestor.pos_,
                        "lemma_c": ancestor.lemma_                     
                    })
                if (ancestor.pos_ == "NOUN" or ancestor.pos_ == "PROPN") and (noun in token.text or noun in ancestor.text):                    
                    dependencies.append({
                        "head": token.text,
                        "child": ancestor.text,
                        "dep_h": token.dep_,
                        "pos_h": token.pos_,
                        "lemma_h": token.lemma_,
                        "dep_c": ancestor.dep_,
                        "pos_c": ancestor.pos_,
                        "lemma_c": ancestor.lemma_
                    })
    
    return dependencies


def get_gendered_for_entity(doc, entity):
    
    doc = merge_phrases(doc)
    # Find the span in the main document corresponding to the entity
    for token in doc:
        if entity.lower() in token.text.lower():
            gender = token.morph.get("Gender", None)
            if gender:
                if gender[0] == "Fem":
                    return "female"
                elif gender[0] == "Masc":
                    return "male"

            related_tokens = set(token.children)
            related_tokens.update({token.head})
            related_tokens.update({child for t in related_tokens for child in t.children}) 
            for related_token in related_tokens:
                gender = related_token.morph.get("Gender", None)
                if gender:
                    if gender[0] == "Fem":
                        return "female"
                    elif gender[0] == "Masc":
                        return "male"
                            
    # If gender cannot be determined
    return "unknown"

def get_gendered_for_nested_entity(entity_doc):
    for token in entity_doc:
        gender = token.morph.get("Gender", None)
        if gender:
            if gender[0] == "Fem":
                return "female"
            elif gender[0] == "Masc":
                return "male"
    return "unknown"