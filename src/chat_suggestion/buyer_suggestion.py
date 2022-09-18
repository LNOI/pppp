from src.utils.db_utils import execute_raw_query

def is_null(istr:str) -> bool:
    if len(istr) == 0 or istr in ['None']:
        return True
    return False

def info_presenting(istr:str) -> str:
    if is_null(istr):
        return 'Thông tin chưa được cập nhật'
    else:
        return istr

def get_buyer_contact(user_id:int) -> dict[str,str]:
    query = 'select full_name, address, phone_number from account_user au where au.id = :user_id'
    res = execute_raw_query(query, user_id=user_id)
    if len(res) > 0:
        username = str(res[0][0])
        address = str(res[0][1])
        phone_number = str(res[0][2])
        if is_null(username) and is_null(address) and is_null(phone_number):
            return {
            'text':'Gửi thông tin giao hàng',
            'value':'Vui lòng hoàn tất thông tin của bạn ở tab Profile để sử dụng chức năng này.'
        }
        return {
            'text':'Gửi thông tin giao hàng',
            'value':'''Thông tin giao hàng
Tên khách hàng: %s
Địa chỉ: %s
SĐT: %s''' % (info_presenting(username), info_presenting(address), info_presenting(phone_number))
        }
    else:
        return {
            'text':'Gửi thông tin giao hàng',
            'value':'Vui lòng hoàn tất thông tin của bạn ở tab Profile để sử dụng chức năng này.'
        }

def buyer_suggestion(user_id:int) -> list[dict[str,str]]:
    content = [
        # get_buyer_contact(user_id),
        {
            'text':'Mình đặt mua sản phẩm này',
            'value':'Mình đặt mua sản phẩm này'
        },
        {
            'text':'Bạn ơi món hàng này còn không',
            'value':'Bạn ơi món hàng này còn không'
        },
        {
            'text':'Bạn ơi mình muốn hỏi thêm về sản phẩm',
            'value':'Bạn ơi mình muốn hỏi thêm về sản phẩm'
        },
        {
            'text':'Bạn ơi shop mình có ship COD không ạ',
            'value':'Bạn ơi shop mình có ship COD không ạ'
        }
    ]
    return content