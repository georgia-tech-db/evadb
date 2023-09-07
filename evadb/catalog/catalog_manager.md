# Catalog Manager

CatalogManager class provides a set of services to interact with a database that stores metadata about tables, columns, and user-defined functions. Information like what is the data type in a certain column in a table, type of a table, its name, etc.. It contains functions to get, insert and delete catalog entries for Tables, Functions, Function IOs, Columns and Indexes.  

This data is stored in the eva_catalog.db file which can be found in `evadb_data` folder.  


Catalog manager currently has 7 services in it:  
```
TableCatalogService()
ColumnCatalogService()  
IndexCatalogService() 
FunctionCatalogService()  
FunctionIOCatalogService()  
FunctionCostCatalogService() 
FunctionMetadataCatalogService()
```

## Catalog Services  
This class provides functionality related to a table catalog, including inserting, getting, deleting, and renaming table entries, as well as retrieving all entries. e.g. the TableCatalogService contains code to get, insert and delete a table.  

## Catalog Models  
These contain the data model that is used by the catalog services.  
Each model represents a table in the underlying database.  

### TableCatalog  
Fields: 
```
name: str  
file_url: str  
table_type: TableType  
identifier_column: str
columns: List[ColumnCatalogEntry]
row_id: int
```

### ColumnCatalog
Fields:  
```
name: str  
type: ColumnType  
is_nullable: bool
array_type: NdArrayType 
array_dimensions: Tuple[int]
table_id: int  
table_name: str 
row_id: int 
```

### IndexCatalog
Fields:  
```
name: str  
save_file_path: str  
type: VectorStoreType  
row_id: int 
feat_column_id: int
function_signature: str 
feat_column: ColumnCatalogEntry 
```
### FunctionCatalog
Fields:  
```
name: str  
impl_file_path: str  
type: str  
row_id: int
args: List[FunctionIOCatalogEntry]
outputs: List[FunctionIOCatalogEntry]  
```
### FunctionIOCatalog
Fields:  
```
name: str  
type: ColumnType  
is_nullable: bool 
array_type: NdArrayType
array_dimensions: Tuple[int] 
is_input: bool  
function_id: int  
function_name: str  
row_id: int  
```

### FunctionCostCatalog
Fields:  
```
function_id: int
name: str
cost: float
row_id: int
```

### FunctionMetadataCatalog
Fields:  
```
key: str
value: str
function_id: int
function_name: str
row_id: int 
```