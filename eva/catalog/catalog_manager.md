# Catalog Manager
Explanation for developers on how to use the eva catalog_manager.

CatalogManager class that provides a set of services to interact with a database that stores metadata about tables, columns, and user-defined functions (UDFs). Information like what is the data type in a certain column in a table, type of a table, its name, etc.. It contains functions to get, insert and delete catalog entries for Tables, UDFs, UDF IOs, Columns and Indexes.  

This data is stored in the eva_catalog.db file which can be found in ~/.eva/<version>/ folder.  

Catalog manager currently has 5 services in it:  
```
TableCatalogService()
ColumnCatalogService()  
UdfCatalogService()  
UdfIOCatalogService()  
IndexCatalogService()  
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
identifier_column: str = "id"  
columns: List[ColumnCatalogEntry] = field(compare=False, default_factory=list)  
row_id: int = None  
```

### ColumnCatalog
Fields:  
```
name: str  
type: ColumnType  
is_nullable: bool = False  
array_type: NdArrayType = None  
array_dimensions: Tuple[int] = field(default_factory=tuple)  
table_id: int = None  
table_name: str = None  
row_id: int = None  
```

### IndexCatalog
Fields:  
```
name: str  
save_file_path: str  
type: IndexType  
row_id: int = None  
feat_column_id: int = None  
udf_signature: str = None  
feat_column: ColumnCatalogEntry = None  
```
### UdfCatalog
Fields:  
```
name: str  
impl_file_path: str  
type: str  
row_id: int = None  
args: List[UdfIOCatalogEntry] = field(compare=False, default_factory=list)  
outputs: List[UdfIOCatalogEntry] = field(compare=False, default_factory=list)  
```
### UdfIOCatalog
Fields:  
```
name: str  
type: ColumnType  
is_nullable: bool = False  
array_type: NdArrayType = None  
array_dimensions: Tuple[int] = None  
is_input: bool = True  
udf_id: int = None  
udf_name: str = None  
row_id: int = None  
```
