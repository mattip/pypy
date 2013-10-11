from rpython.annotator import model as annmodel
from rpython.annotator.listdef import ListDef
from rpython.rlib.objectmodel import specialize
from rpython.rlib import jit
from rpython.rtyper.lltypesystem import lltype, llmemory
from rpython.rtyper.extregistry import ExtRegistryEntry
from rpython.tool.pairtype import pair

def copy_list_to_raw_array(lst, array):
    for i, item in enumerate(lst):
        array[i] = item

def populate_list_from_raw_array(lst, array, length):
    lst[:] = [array[i] for i in range(length)]



class Entry(ExtRegistryEntry):
    _about_ = copy_list_to_raw_array

    def compute_result_annotation(self, *s_args):
        pass

    def specialize_call(self, hop):
        hop.exception_cannot_occur()
        v_list, v_buf = hop.inputargs(*hop.args_r)
        return hop.gendirectcall(ll_copy_list_to_raw_array, v_list, v_buf)


class Entry(ExtRegistryEntry):
    _about_ = populate_list_from_raw_array

    def compute_result_annotation(self, s_list, s_array, s_length):
        s_item = annmodel.lltype_to_annotation(s_array.ll_ptrtype.TO.OF)
        s_newlist = self.bookkeeper.newlist(s_item)
        s_newlist.listdef.resize()
        pair(s_list, s_newlist).union()

    def specialize_call(self, hop):
        v_list, v_buf, v_length = hop.inputargs(*hop.args_r)
        hop.exception_is_here()
        return hop.gendirectcall(ll_populate_list_from_raw_array, v_list, v_buf, v_length)


@specialize.ll()
def get_raw_buf(ptr):
    ofs = llmemory.itemoffsetof(lltype.typeOf(ptr).TO, 0)
    return llmemory.cast_ptr_to_adr(ptr) + ofs
get_raw_buf._always_inline_ = True


@jit.dont_look_inside
def ll_copy_list_to_raw_array(ll_list, dst_ptr):
    # this code is delicate: we must ensure that there are no GC operations
    # around the call to raw_memcopy
    #
    ITEM = lltype.typeOf(dst_ptr).TO.OF
    size = llmemory.sizeof(ITEM) * ll_list.ll_length()
    # start of no-GC section
    src_adr = get_raw_buf(ll_list.ll_items())
    dst_adr = get_raw_buf(dst_ptr)
    llmemory.raw_memcopy(src_adr, dst_adr, size)
    # end of no-GC section


@jit.dont_look_inside
def ll_populate_list_from_raw_array(ll_list, src_ptr, length):
    ITEM = lltype.typeOf(src_ptr).TO.OF
    size = llmemory.sizeof(ITEM) * length
    ll_list._ll_resize(length)
    # start of no-GC section
    src_adr = get_raw_buf(src_ptr)
    dst_adr = get_raw_buf(ll_list.ll_items())
    llmemory.raw_memcopy(src_adr, dst_adr, size)
    # end of no-GC section
