
#get the optimal plan
#go to the children attribute
#types seqscan, project, predicate, lateral join, functional scan

#target list has the list of columns that need to be selected

#Lateral Join: Children traverse sequential and join.
#Seq Scan: 


import sys
from eva.planner import SeqScanPlan, LateralJoinPlan, StoragePlan, FunctionScanPlan, ProjectPlan


if sys.version_info >= (3, 8):
    from functools import singledispatchmethod
else:
    # https://stackoverflow.com/questions/24601722/how-can-i-use-functools-singledispatch-with-instance-methods
    from functools import singledispatch, update_wrapper

    def singledispatchmethod(func):
        dispatcher = singledispatch(func)

        def wrapper(*args, **kw):
            return dispatcher.dispatch(args[1].__class__)(*args, **kw)

        wrapper.register = dispatcher.register
        update_wrapper(wrapper, func)
        return wrapper




class ColumnDeriver:

    def __init__(self):
        pass

    def merge(self, lst1, dict1, lst2, dict2):
        pass
    

    @singledispatchmethod
    def scan_node(self, node, prefix=None):
        raise NotImplementedError(f"Cannot bind {type(node)}")

    @scan_node.register(ProjectPlan)
    def scan_node(self, node, prefix=None):
        child_nodes = node.children
        if len(child_nodes)>0:
            id_list, id_map = self.scan_node(child_nodes[0])

        return id_list, id_map
    
    @scan_node.register(StoragePlan)
    def scan_node(self, node, prefix=None):
        video_columns = node.columns
        col_name_to_id_mapping = {}
        id_list = []
        id_counter = 0
        for column in video_columns:
            if prefix:
                col_name = prefix+column.name
            if col_name not in col_name_to_id_mapping:
                col_name_to_id_mapping[col_name] = id_counter
                id_list.append(id_counter)
                id_counter+=1
        
        return id_list, col_name_to_id_mapping

    @scan_node.register(SeqScanPlan)
    def scan_node(self, node, prefix=None):
        alias_name = node.alias_name
        id_list, id_map = self.scan_node(node.children[0], alias_name)
        return id_list, id_map

    @scan_node.register(LateralJoinPlan)
    def scan_node(self,node, prefix=None):
        left_list, left_map = self.scan_node(node.children[0])
        right_list, right_map = self.scan_node(node.children[0])

        merged_list = left_list[:]
        merged_map = left_map
        counter = len(left_list)
        
        #merging the two lists
        new_map = {}
        for col_name, col_id in right_map:
            if col_name in left_map:
                new_map[col_id] = left_map[col_name]
            else:
                new_map[col_id] = counter
                merged_map[col_name] = counter
                counter+=1
        
        for i, id_val in enumerate(right_list):
            right_list[i] = new_map[id_val]
        
        merged_list.extend(right_list)
        return merged_list, merged_map






        

        

        




        

    