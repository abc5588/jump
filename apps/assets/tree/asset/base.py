import abc
from data_tree import Data_tree_node

__all__ = ['TreeNode', 'BaseAssetTree']


delimiter_for_path = ':'
path_key_of_asset = '.'


class TreeNode(Data_tree_node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BaseAssetTree(object):
    """ 基本的资产节点树 """
    def __init__(self, **kwargs):
        self._root = TreeNode(arg_string_delimiter_for_path=delimiter_for_path)

    @abc.abstractmethod
    def initial(self):
        """ 初始化树 """
        raise NotImplemented

    @staticmethod
    def append_path_to_tree_node(tree_node, arg_path, arg_node=None) -> TreeNode:
        """
        添加路径到 tree_node
        arg - tree_node: instance of TreeNode
        arg - arg_path: str
        arg - arg_node: None or instance of TreeNode
        """
        _tree_node = tree_node.append_path(arg_path=arg_path, arg_node=arg_node)
        return _tree_node

    def get_tree_node_at_path(self, arg_path) -> TreeNode:
        """ 根据路径获取 tree_node """
        _tree_node = self._root.get_node_child_at_path(arg_path=arg_path)
        return _tree_node

    def count_assets(self):
        """ 计算所有的资产数量 """
        assets_id = self.get_assets_id()
        return len(assets_id)

    def count_assets_of_node(self, node_key, immediate=False):
        """
        计算节点下的资产数量

        arg - node_key:
        arg - immediate: if True: 只计算节点的直接资产; else: 计算节点下的所有资产;
        """
        assets_id = self.get_assets_id_of_node(node_key=node_key, immediate=immediate)
        return len(set(assets_id))

    def count_nodes(self, level=None):
        """ 计算所有节点的数量 """
        nodes_key = self.get_nodes_key(level=level)
        return len(nodes_key)

    def count_node_children(self, node_key, level=None):
        node_children_key = self.get_node_children_key(node_key=node_key, level=level)
        return len(node_children_key)

    def get_assets_id(self):
        """ 获取所有资产id """
        assets_id = self.paths_assets(asset_id_as_path=True)
        return list(set(assets_id))

    def get_assets_id_of_node(self, node_key, immediate=False):
        """ 获取节点下的资产id """
        assets_id = self.paths_assets_of_node(
            node_key=node_key, immediate=immediate, asset_id_as_path=True
        )
        return list(set(assets_id))

    def get_nodes_key(self, level=None):
        nodes_key = self.paths_nodes(level=level)
        return nodes_key

    def get_nodes_children_key(self, nodes_key):
        nodes_children_key = set()
        for node_key in nodes_key:
            node_children_key = self.get_node_children_key(node_key=node_key)
            nodes_children_key.update(node_children_key)
        return list(nodes_children_key)

    def get_node_children_key(self, node_key, level=None):
        """ 获取子孙节点的key """
        node_children_key = self.paths_node_children(node_key=node_key, level=level)
        return node_children_key

    def paths_nodes(self, level=None):
        """ 获取所有 nodes 的路径 """
        return self.paths_node_children(node_key=None, level=level)

    def paths_node_children(self, node_key=None, level=None):
        """
        return: 返回节点的子节点的路径
        arg: node_key - 节点key
        arg: immediate - 是否是直接子节点
        """

        assert level is None or isinstance(level, int), '`level` should be of type int or None'

        if level == 0:
            return []

        if level == 1:
            _arg_bool_search_sub_tree = False
        else:
            _arg_bool_search_sub_tree = False

        if node_key is None:
            _tree_node = self._root
        else:
            _tree_node = self.get_tree_node_at_path(arg_path=node_key)

        if _tree_node is None:
            return []

        _arg_callable_filter = self.__arg_callable_filter_for_node_path
        _arg_callable_formatter = self.__arg_callable_formatter_for_path_as_iterable

        paths = self.paths_of_tree_node(
            tree_node=_tree_node,
            arg_bool_search_sub_tree=_arg_bool_search_sub_tree,
            arg_callable_filter=_arg_callable_filter,
            arg_callable_formatter=_arg_callable_formatter
        )

        if level is None:
            _to_filter_level = False
        else:
            _to_filter_level = True

        if _to_filter_level:
            paths = [path for path in paths if len(path) <= level]

        if _tree_node is self._root:
            _is_absolute_path = True
        else:
            _is_absolute_path = False

        if not _is_absolute_path:
            paths = [self._iterable_path_as_string([node_key, path]) for path in paths]

        return paths

    def paths_assets(self, asset_id_as_path=False):
        """ 所有资产的路径 """
        return self.paths_assets_of_node(asset_id_as_path=asset_id_as_path)

    def paths_assets_of_node(self, node_key=None, immediate=False, asset_id_as_path=False):
        """
        return: 返回节点下的资产的路径
        arg: node_key - 节点 key
        arg: immediate - 是否是直接资产
        arg: only_asset_id - 是否只返回资产id
        """

        if node_key is None:
            _tree_node = self._root
        else:
            _tree_node = self.get_tree_node_at_path(arg_path=node_key)

        if _tree_node is None:
            return []

        if immediate:
            _arg_bool_search_sub_tree = True
        else:
            _arg_bool_search_sub_tree = False

        if asset_id_as_path:
            _arg_callable_formatter = self.__arg_callable_formatter_for_asset_id_as_path
        else:
            _arg_callable_formatter = self.__arg_callable_formatter_for_path_as_string

        _arg_callable_filter = self.__arg_callable_filter_for_asset_path

        paths = self.paths_of_tree_node(
            tree_node=_tree_node,
            arg_bool_search_sub_tree=_arg_bool_search_sub_tree,
            arg_callable_filter=_arg_callable_filter,
            arg_callable_formatter=_arg_callable_formatter
        )

        if asset_id_as_path:
            _to_absolute_path = False
        else:
            _to_absolute_path = True

        if _tree_node is self._root:
            _is_absolute_path = True
        else:
            _is_absolute_path = False

        if _to_absolute_path and not _is_absolute_path:
            paths = [delimiter_for_path.join([node_key, path]) for path in paths]

        return paths

    def paths_assets_of_assets_id(self, assets_id):
        """ 获取多个资产的所有路径 """

        _arg_callable_filter = self.__arg_callable_filter_for_asset_path
        _arg_callable_formatter = self.__arg_callable_formatter_for_path_as_iterable

        paths_assets = self.paths_of_tree_node(
            tree_node=self._root,
            arg_callable_filter=_arg_callable_filter,
            arg_callable_formatter=_arg_callable_formatter
        )
        paths_assets = [asset_path for asset_path in paths_assets if asset_path[-1] in assets_id]
        paths = [self._iterable_path_as_string(iterable_path=path) for path in paths_assets]
        return paths

    def paths_of_tree_node(self, tree_node: TreeNode, **kwargs) -> list:
        """ 获取 tree_node 节点下的路径 """
        _default_arg_callable_formatter = self.__arg_callable_formatter_for_path_as_string

        _arg_bool_search_sub_tree = kwargs.get('arg_bool_search_sub_tree', True)
        _arg_callable_filter = kwargs.get('arg_callable_filter')
        _arg_callable_formatter = kwargs.get('arg_callable_formatter')
        _arg_callable_formatter = _arg_callable_formatter or _default_arg_callable_formatter

        paths = tree_node.get_list_of_pairs_paths_and_node_children(
            arg_bool_search_sub_tree=_arg_bool_search_sub_tree,
            arg_callable_filter=_arg_callable_filter,
            arg_callable_formatter=_arg_callable_formatter
        )
        return paths

    @staticmethod
    def _iterable_path_as_string(iterable_path):
        return delimiter_for_path.join(iterable_path)

    @staticmethod
    def __arg_callable_filter_for_node_path(arg_iterable_path, arg_node):
        return ''.join(arg_iterable_path).isdigit()

    @staticmethod
    def __arg_callable_filter_for_asset_path(arg_iterable_path, arg_node):
        if path_key_of_asset not in arg_iterable_path:
            return False
        index_for_path_key_of_asset = arg_iterable_path.index(path_key_of_asset)
        index_for_asset_id = index_for_path_key_of_asset + 1
        return len(arg_iterable_path) == index_for_asset_id + 1

    @staticmethod
    def __arg_callable_formatter_for_path_as_string(arg_iterable_path, arg_node):
        return delimiter_for_path.join(arg_iterable_path)

    @staticmethod
    def __arg_callable_formatter_for_path_as_iterable(arg_iterable_path, arg_node):
        return arg_iterable_path

    @staticmethod
    def __arg_callable_formatter_for_asset_id_as_path(arg_iterable_path, arg_node):
        index_of_path_key_of_asset = arg_iterable_path.index(path_key_of_asset)
        index_of_asset_id = index_of_path_key_of_asset + 1
        asset_id = arg_iterable_path[index_of_asset_id]
        return asset_id
