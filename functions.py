import re
import requests
import subprocess

url = "https://api-gateway.skymavis.com/graphql/marketplace"
headers = {
"Content-Type": "application/json",
"X-API-Key": "get your own key at developers.skymavis.com/"
}

#purity score is 76-100
def get_purity(hexgene):
    genes = hexgene_to_genes(hexgene)
    dominant = []
    dominant.append('nothing important')
    i = 1
    while i < 7:
        dominant.append(genes[i][0])
        i = i + 1
    purity_complement = 0
    i = 1
    while i < 7:
        if genes[i][1] != dominant[i]:
            purity_complement = purity_complement + 3
        if genes[i][2] != dominant[i]:
            purity_complement = purity_complement + 1
        i = i + 1
    purity = 100 - purity_complement
    return(purity)


def get_c_score(hexgene1, hexgene2):
    genes1 = hexgene_to_genes(hexgene1)
    genes2 = hexgene_to_genes(hexgene2)
    dominant = []
    dominant.append('nothing important')
    i = 1
    while i < 7:
        dominant.append(genes1[i][0])
        i = i + 1
    c_score = 0
    i = 1
    while i < 7:
        if genes1[i][1] != dominant[i] and genes2[i][1] != dominant[i]:
            c_score = c_score + 3
        if genes1[i][2] != dominant[i] and genes2[i][2] != dominant[i]:
            c_score = c_score + 1
        i = i + 1
    return(c_score)

#[0] = cls, [1-6] = mouth to tail, input = hexgene, output = genes
def hexgene_to_genes(hexgene):
    js_code_template = """
    const { AxieGene } = require("agp-npm/dist/axie-gene");
    const hex = "%s";
    const axieGene = new AxieGene(hex);
    console.log(axieGene.genes.cls);
    console.log(axieGene.genes.mouth.d.partId);
    console.log(axieGene.genes.mouth.r1.partId);
    console.log(axieGene.genes.mouth.r2.partId);
    console.log(axieGene.genes.eyes.d.partId);
    console.log(axieGene.genes.eyes.r1.partId);
    console.log(axieGene.genes.eyes.r2.partId);
    console.log(axieGene.genes.horn.d.partId);
    console.log(axieGene.genes.horn.r1.partId);
    console.log(axieGene.genes.horn.r2.partId);
    console.log(axieGene.genes.ears.d.partId);
    console.log(axieGene.genes.ears.r1.partId);
    console.log(axieGene.genes.ears.r2.partId);
    console.log(axieGene.genes.back.d.partId);
    console.log(axieGene.genes.back.r1.partId);
    console.log(axieGene.genes.back.r2.partId);
    console.log(axieGene.genes.tail.d.partId);
    console.log(axieGene.genes.tail.r1.partId);
    console.log(axieGene.genes.tail.r2.partId);
    // ... add more code as required ...
    """
    js_code = js_code_template % hexgene
    result = subprocess.run(['node', '-e', js_code], capture_output=True, text=True)
    string = result.stdout
    string_list = string.split('\n')
    genes = []
    genes.append(string_list[0])
    i = 1
    while i < 19:
        j = 0
        part_gene = []
        while j < 3:
            gene_raw = string_list[i]
            if i < 4: 
                part_gene.append(gene_raw[6:]) #6:
            else:
                part_gene.append(gene_raw[5:]) #5:
            j = j + 1
            i = i + 1
        genes.append(part_gene)
    return genes

#input: ronin and parts_list, output: breed_pool of virgins
def searchronin_from_partslist(owner_address, parts_list, classes):
    query = """
    query MyQuery($owner: String!, $parts: [String!]!, $classes: [AxieClass!]) {
      axies(owner: $owner, criteria: { parts: $parts, breedCount: 0, classes: $classes } size: 100) {
        total
        results {
          id
          genes
          sireId
          matronId
          class
          breedCount
          image
        }
      }
    }
    """
    variables = {
        "owner": owner_address,
        "classes": classes,
        "parts": parts_list
        
    }
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        axies_data = data.get("data", {}).get("axies", {}).get("results", [])
        return [[axie["id"], axie["genes"], axie["class"], axie["breedCount"], axie["sireId"], axie["matronId"]] for axie in axies_data]
    else:
        print("GraphQL request failed with status code:", response.status_code)
        return []
    
def get_virgin_details(id):
    query = """
    query MyQuery($axieId: ID!) {
    axie(axieId: $axieId) {
        id
        genes
        sireId
        matronId
        class
        breedCount
        image
    }
    }
    """
    variables = {"axieId": id}
  
    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    data = response.json()    
    axies_data = data.get("data", {}).get("axie", {})
    attributes = [
      axies_data.get("id"),
      axies_data.get("genes"),
      axies_data.get("class"),
      axies_data.get("breedCount"),
      axies_data.get("sireId"),
      axies_data.get("matronId")
    ]
    return(attributes)



def url_to_parts(url):
    matches = re.findall(r"parts=(\w+)-(\w+(?:-\w+)?)", url) # Find all the parts and values in the URL, with the first word as the part name and the second word as the value, with an optional second word after a hyphen
    parts_dict = {part: value.replace('-', ' ') for part, value in matches} # Create a dictionary that maps the parts to the values, replacing the hyphen with a space if present
    return parts_dict

#long format is like [mouth-doubletalk], used to ask API for specific axies
def partsdict_to_parts_long(partsdict):
    parts = []
    mouth = 'mouth-'+partsdict['mouth'];mouth = mouth.replace(" ", "-");parts.append(mouth)
    eye = 'eyes-'+partsdict['eyes'];eye = eye.replace(" ", "-");parts.append(eye)
    horn = 'horn-'+partsdict['horn'];horn = horn.replace(" ", "-");parts.append(horn)
    ear = 'ears-'+partsdict['ears'];ear = ear.replace(" ", "-");parts.append(ear)
    back = 'back-'+partsdict['back'];back = back.replace(" ", "-");parts.append(back)
    tail = 'tail-'+partsdict['tail'];tail = tail.replace(" ", "-");parts.append(tail)
    return(parts)

#short format is like [doubletalk], good if just parts names are needed
def partsdict_to_parts_short(partsdict):
    parts = []
    mouth = partsdict['mouth'];mouth = mouth.replace(" ", "-");parts.append(mouth)
    eye = partsdict['eyes'];eye = eye.replace(" ", "-");parts.append(eye)
    horn = partsdict['horn'];horn = horn.replace(" ", "-");parts.append(horn)
    ear = partsdict['ears'];ear = ear.replace(" ", "-");parts.append(ear)
    back = partsdict['back'];back = back.replace(" ", "-");parts.append(back)
    tail = partsdict['tail'];tail = tail.replace(" ", "-");parts.append(tail)
    return(parts)

def parts_to_url():
    return('hello for now')

def get_axie_image(parts):
    parts_list = []
    mouth = str('mouth-' + parts['mouth']).replace(" ", "-")
    eyes = str('eyes-' + parts['eyes']).replace(" ", "-")
    horn = str('horn-' + parts['horn']).replace(" ", "-")
    ears = str('ears-' + parts['ears']).replace(" ", "-")
    back = str('back-' + parts['back']).replace(" ", "-")
    tail = str('tail-' + parts['tail']).replace(" ", "-")
    parts_list.extend([mouth, eyes, horn, ears, back, tail])
    parts_list_str = ', '.join(['"' + part + '"' for part in parts_list])

    query = f'''
    query MyQuery {{
      axies(
        criteria: {{parts: [{parts_list_str}]}}
        auctionType: All
      ) {{
        results {{
          id
          image
        }}
      }}
    }}
    '''

    response = requests.post(url, headers=headers, json={"query": query})
    data = response.json()
    axies = data.get('data', {}).get('axies', {}).get('results', [])
    
    if axies:
        axie_id = axies[0]['id']
        image = f"https://axiecdn.axieinfinity.com/axies/{axie_id}/axie/axie-full-transparent.png"
        return image
    else:
        print("No Axies found with the specified parts.")
        return None

#query and get details given axie id
def get_axie_details(id):
    query = """
    query MyQuery($axieId: ID!) {
    axie(axieId: $axieId) {
        birthDate
        class
        genes
        breedCount
        image
        parts {
        name
        class
        }
        stage
    }
    }
    """
    variables = {"axieId": id}
    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    data = response.json()
    axieId = id
    birthDate = data['data']['axie']['birthDate']
    stage = data['data']['axie']['stage']
    if stage == 4:
        axieClass = data['data']['axie']['class']
        genes = data['data']['axie']['genes']
        breedCount = data['data']['axie']['breedCount']
        imageUrl = "https://axiecdn.axieinfinity.com/axies/" + str(axieId) + "/axie/axie-full-transparent.png"
        marketplaceUrl = "https://app.axieinfinity.com/marketplace/axies/" + str(axieId)
        eye = data['data']['axie']['parts'][0]['name']
        ear = data['data']['axie']['parts'][1]['name']
        back = data['data']['axie']['parts'][2]['name']
        mouth = data['data']['axie']['parts'][3]['name']
        horn = data['data']['axie']['parts'][4]['name']
        tail = data['data']['axie']['parts'][5]['name']
        eye_class = data['data']['axie']['parts'][0]['class']
        ear_class = data['data']['axie']['parts'][1]['class']
        back_class = data['data']['axie']['parts'][2]['class']
        mouth_class = data['data']['axie']['parts'][3]['class']
        horn_class = data['data']['axie']['parts'][4]['class']
        tail_class = data['data']['axie']['parts'][5]['class']
        details = []
        details.append(axieId)
        details.append(birthDate)
        details.append(axieClass)
        details.append(genes)
        details.append(breedCount)
        details.append(imageUrl)
        details.append(marketplaceUrl)
        details.append(mouth_class)
        details.append(eye_class)
        details.append(horn_class)
        details.append(ear_class)
        details.append(back_class)
        details.append(tail_class)
        details.append(mouth)
        details.append(eye)
        details.append(horn)
        details.append(ear)
        details.append(back)
        details.append(tail)
    else:
        details = []
        details.append(axieId)
        details.append(birthDate)
        details.append(marketplaceUrl)
        details.append("EGG")
    return(details)
