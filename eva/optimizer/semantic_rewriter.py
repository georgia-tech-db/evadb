from enum import Enum
from torch import Tensor, device
import torch
import uuid
import pandas as pd
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
import numpy as np
import os
import openai
from transformers import AutoTokenizer, AutoModel
# from eva.parser.table_ref import TableInfo
from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import TableType
from eva.udfs.yolo_object_detector import YoloV5
from eva.catalog.catalog_type import ColumnType

encoding_model_name = 'shahrukhx01/paraphrase-mpnet-base-v2-fuzzy-matcher'
encoding_model = AutoModel.from_pretrained(encoding_model_name).to(torch_device)
encoding_tokenizer = AutoTokenizer.from_pretrained(encoding_model_name)

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.getenv("OPENAI_API_KEY")

UDFSupport = [
   YoloV5
]

class SemanticRewriter:
    def __init__(self, text, table_name):
        self.text = text
        self.prompt = ''
        self.table_name = table_name
        self.rows = []
        self.header = []
        self.header_types = []

    def generate_tables(self):
      catalog = CatalogManager()
      table_name = self.table_name
      database_name = "database"

      table_catalog = catalog.get_table_catalog_entry(
          table_name,
          database_name,
      )

      print(table_catalog)

      if table_catalog is None:
         return "InvalidTableName{\}"

      table_type = getattr(table_catalog, 'table_type')
      accessory_name = []
      accessory_type = []
      accessory_row = []
      
      if table_type == TableType.VIDEO_DATA:
        yolo = YoloV5()
        accessory_name = yolo.labels
        accessory_type = ['YoloV5-label' for name in accessory_name]
        accessory_row = ['nan' for name in accessory_name]
        accessory_name += ['frame', 'scores']
        accessory_type += ['frame', ColumnType.FLOAT]
        accessory_row += ['nan', 'nan']
        

      columns = getattr(table_catalog, 'columns')
      # select_query = f"""SELECT * FROM {table_name};"""
      # batch = execute_query_fetch_all(select_query)
      # rows = batch.frames().values.tolist()
      col_name = [getattr(column, 'name') for column in columns] + accessory_name

      col_type = ['text' if (getattr(column, 'type') == ColumnType.TEXT or getattr(column, 'type') == ColumnType.BOOLEAN) else 'numeric' if (getattr(column, 'type') == ColumnType.INTEGER or getattr(column, 'type') == ColumnType.FLOAT) else 'other' for column in columns] + accessory_type
      
      #rows = [row + accessory_row for row in rows]

      #self.rows = rows
      self.header = col_name
      self.header_types = col_type

      return f"{table_name}(" + ", ".join(col_name) + ")"
    
    def rewrite(self, header=None, header_types=None):
        self.prompt = "### Postgres SQL tables, with their properties:\n#\n#{tables}\n#\n### {text}\nSELECT".format(tables=self.generate_tables(), text=self.text)
        return self.prompt

class QueryProcessor():
    def __init__(self, rows, header, header_types, prompt):
        self.rows = rows
        self.header = header
        self.header_types = header_types
        self.prompt = prompt
        self.response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=150,
            
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["#", ";"]
        )
        self.prediction = 'SELECT' + str(self.response['choices'][0]['text'])
        self.sql_operators = ['>', '=', '<', '>=', '<=', '<>']
        self.agg_operators = ['MAX', 'AVG', 'MIN', 'COUNT', 'SUM']
        self.rule_cond = {'YoloV5-label': self.yololabel_cond}
        self.rule_agg = {'YoloV5-label': self.yololabel_agg, 'frame': self.Frame}


    ## define the helper functions below
    def table_processor(self):
        idx = []
        for i in range(len(self.header)):
          if self.header_types[i] != 'text':
            idx.append(i)

        r = np.array(self.rows)
        h = np.array(self.header)
        t = np.array(self.header_types)

        r = np.delete(r, idx, axis=1)
        h = np.delete(h, idx, axis=0)
        t = np.delete(t, idx, axis=0) 

        return (list(r), list(h), list(t))


    def cos_sim(a: Tensor, b: Tensor):
        """
        borrowed from sentence transformers repo
        Computes the cosine similarity cos_sim(a[i], b[j]) for all i and j.
        :return: Matrix with res[i][j]  = cos_sim(a[i], b[j])
        """
        if not isinstance(a, torch.Tensor):
            a = torch.tensor(a)

        if not isinstance(b, torch.Tensor):
            b = torch.tensor(b)

        if len(a.shape) == 1:
            a = a.unsqueeze(0)

        if len(b.shape) == 1:
            b = b.unsqueeze(0)

        a_norm = torch.nn.functional.normalize(a, p=2, dim=1)
        b_norm = torch.nn.functional.normalize(b, p=2, dim=1)
        return torch.mm(a_norm, b_norm.transpose(0, 1))


    #Mean Pooling - Take attention mask into account for correct averaging
    def mean_pooling(self,model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    ## get embedding of a word
    def get_embedding(self, value):
        value = value.lower()
        value = [" ".join([x for x in value])]
        # Tokenize sentences
        encoded_input = encoding_tokenizer(value, padding=True, truncation=True, return_tensors='pt').to(torch_device)

        # Compute token embeddings
        with torch.no_grad():
            model_output = encoding_model(**encoded_input)

        # Perform pooling. In this case, max pooling.
        embedding = self.mean_pooling(model_output, encoded_input['attention_mask'])
        return embedding

    ## encodes categorical data into vector space
    def encode_data(self, data, header, header_types):
        table = pd.DataFrame(data, columns=header)
        data = {}
        #cell = " ".join([x for x in generated_data])
        for header_val, header_type_val in zip(header, header_types):
            encoded_vals = Tensor().to(torch_device)
            if header_type_val == 'text':
                for value in table[header_val]:
                    #encoded_vals.append()
                    encoded_vals  = torch.cat((encoded_vals, self.get_embedding(value)), 0)
            data[header_val] = encoded_vals.cpu()
        return data, table

    ## external memory lookup
    def memory_lookup(self, embeddings, query_value, column_values, lookup_map, column_map, cond_col, threshold=1.0):
        lookup_value = None
        query_value = query_value.replace('`','').strip()
        sorted_sim, index = self.compute_cosine(query_value, embeddings)
        if sorted_sim >= .70:
            lookup_value = column_values[index]
        else:
            for col in list(lookup_map.keys()):
                embeddings = lookup_map[col]
                sorted_sim, index = self.compute_cosine(query_value, embeddings)
                if sorted_sim >= .95:
                    lookup_value = column_map[col].vlaues[index]
                    cond_col = col
                break
        return (cond_col, lookup_value)

    ## compute cosine similarity between matrix of candidattes and a query vector      
    def compute_cosine(self, query_value, embeddings):
        query_embedding = self.get_embedding(query_value).to(torch_device)
        embeddings = embeddings.to(torch_device)
        
        sim = self.cos_sim(embeddings, query_embedding)
        sorted_sim, indices = torch.sort(sim, axis=0, descending=True)
        return sorted_sim[0][0].item(), indices[0][0].item()

    def condition_processor(self, clause, conditions, encoded_data, table, lookup_value):
      for condition in clause:
            column = [(column, idx) for column in condition.strip().split() for idx, col in enumerate(self.header) if col in column]
            operator = None
            if len(column):
                for op in self.sql_operators:
                  if op in condition:
                    operator = op

                if operator:
                  cond_col, operator, con_val = column[0][0], operator, condition.split(operator)[1]
                  cond_col_type = self.header_types[column[0][1]]
                  if cond_col_type in self.rule_cond.keys():
                    conditions.append(self.rule_cond[cond_col_type](cond_col, operator, con_val))  
                  else:
                    if operator == '=' and cond_col_type == 'text':
                      if not lookup_value:
                        cond_col, lookup_value = self.memory_lookup(
                            embeddings=encoded_data[cond_col], 
                            query_value=con_val, 
                            column_values=table[cond_col].values ,
                            lookup_map= encoded_data,
                            column_map=table,
                            cond_col=cond_col,
                            threshold=1.0
                        )
                      else: 
                          lookup_value = con_val.replace('`','').strip()
                      if lookup_value:
                          conditions.append(f"{cond_col} {operator} \'{lookup_value}\'")
                    elif cond_col_type == 'numeric':
                      conditions.append(f"{cond_col} {operator} \'{con_val}\'")
            else:
                break


    def yololabel_cond(self, cond_col, operator, con_val):
      if con_val.strip().isnumeric():
        cond = f"ArrayCount(YoloV5(data).labels, '{cond_col}') {operator} {con_val}"
      else:
        cond = f"['{cond_col}']' <@ YoloV5(data).labels"

      return cond

          
    def yololabel_agg(self, agg_clause, select_col):
      sel = ''
      if agg_clause == 'COUNT':
        sel = f"ArrayCount(YoloV5(data).labels, '{select_col}')"

      return sel


    def Frame(self, agg_clause, select_col):
      sel = ''
      if agg_clause == 'COUNT':
        sel = f"COUNT(*)"
      elif agg_clause == 0:
        tb = select_col.split('.')[0]
        if tb:
          sel = f"{tb}.id, {tb}.data"
        else:
          sel = 'id, data'

      return sel
    ## define sql augment function to resolved the ambigous entities
    
    def query_processor(self, lookup_value):
        
        r, h, t = self.table_processor()

        encoded_data, table = self.encode_data(r, h, t)

        select_clause = self.prediction.split('FROM')[0].strip().split('SELECT')[1].replace(" ", "").split(',')
        agg_clause = [(s.split('(')[0], s.split('(')[-1].split(')')[0]) if s.split('(')[0] in self.agg_operators else (0, s.split('(')[-1].split(')')[0]) for s in select_clause]            
        where_clause = []
        where_conditions = []
        where_final = ''       
        if 'WHERE' in self.prediction:
          where_clause = self.prediction.split('GROUP BY')[0].strip().split('WHERE')[1].split('AND')
          self.condition_processor(where_clause, where_conditions, encoded_data, table, lookup_value) 
          where_final = " AND ".join(where_conditions)     

        groupby_final = ''
        if 'GROUP BY' in self.prediction:
          groupby_final = 'GROUP BY' + self.prediction.split('HAVING')[0].strip().split('GROUP BY')[1]

        having_clause = []
        having_conditions = []
        having_final = ''
        if 'HAVING' in self.prediction:
          having_clause = self.prediction.split('ORDER BY')[0].strip().split('GROUP BY')[1].split('AND')
          self.condition_processor(having_clause, having_conditions, encoded_data, table)
          having_final = " AND ".join(having_conditions)

        select_cols = []
        for clause in agg_clause: 
          if clause[1] != '*':      
            col_type = self.header_types[self.header.index(clause[1])]
                        
            if col_type in self.rule_agg.keys():
              select_col = self.rule_agg[col_type](clause[0], clause[1])
            else:
              if clause[0] != 0:
                select_col = f"{clause[0]}" + "(" + f"{clause[1]}" + ")"
              else:
                select_col = clause[1]
          else:
            if clause[0] != 0:
              select_col = f"{clause[0]}" + "(" + f"{clause[1]}" + ")"  
            else:
              select_col = clause[1]     

          select_cols.append(select_col)
            
        select_final = f"SELECT "+ " , ".join(select_cols)
        table_name = str(uuid.uuid4())
        sql_final = f"{select_final} FROM"
        join_final = self.prediction.split('WHERE')[0].split('FROM')[1]
        order_final = ''
        if 'ORDER BY' in self.prediction:
          order_final = 'ORDER BY' + self.prediction.split('ORDER BY')[1]
        
        sql_final += join_final + f"WHERE {where_final} " + groupby_final + having_final + order_final
        return sql_final