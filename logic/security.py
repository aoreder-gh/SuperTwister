#  /**
#   * Super Twister 3001
#   *
#   * @author    Andreas Reder <aoreder@gmail.com>
#   *
#   * @copyright Andreas Reder
#   * @version   1.0.0
#   */

import hashlib
import state

SERVICE_HASH = "2399144e96a69e6f5f2b14e6b38cf605ede6b92abd49838b0e4d72a74a6c63be"


# service123

def login(password):
    if hashlib.sha256(password.encode()).hexdigest() == SERVICE_HASH:
        state.user_role = "SERVICE"
        return True
    else:
        state.user_role = "OPERATOR"

    return False
