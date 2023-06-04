# Catalog Manager

CatalogManager class provides a set of services to interact with a database that stores metadata about tables, columns, and user-defined functions (UDFs). Information like what is the data type in a certain column in a table, type of a table, its name, etc.. It contains functions to get, insert and delete catalog entries for Tables, UDFs, UDF IOs, Columns and Indexes.  

This data is stored in the eva_catalog.db file which can be found in ~/.eva/<version>/ folder.  

Catalog manager currently has 7 services in it:  
```
TableCatalogService()
ColumnCatalogService()  
IndexCatalogService() 
UdfCatalogService()  
UdfIOCatalogService()  
UdfCostCatalogService() 
UdfMetadataCatalogService()
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
udf_signature: str 
feat_column: ColumnCatalogEntry 
```
### UdfCatalog
Fields:  
```
name: str  
impl_file_path: str  
type: str  
row_id: int
args: List[UdfIOCatalogEntry]
outputs: List[UdfIOCatalogEntry]  
```
### UdfIOCatalog
Fields:  
```
name: str  
type: ColumnType  
is_nullable: bool 
array_type: NdArrayType
array_dimensions: Tuple[int] 
is_input: bool  
udf_id: int  
udf_name: str  
row_id: int  
```

### UdfCostCatalog
Fields:  
```
udf_id: int
name: str
cost: float
row_id: int
```

### UdfMetadataCatalog
Fields:  
```
key: str
value: str
udf_id: int
udf_name: str
row_id: int 
```