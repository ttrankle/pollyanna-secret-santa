
# TODO: update to 3.11 and use StrEnum
class GoogleAuthConstants:
    CREDENTIALS_JSON = "credentials.json"
    TOKEN_JSON = "token.json"

MESSAGE_TEMPLATE = """Ho Ho Ho {name}!

This email is from the Pollyanna (Secret Santa) Program.

You drew the following names:
    Genuine Gift: {gift_name}
    Gag Gift: {gag_name}

Have fun shopping!

P.S. Budgets for the gifts will be sent out at a later date.
Reach out if you received the same name twice.
"""

HTML_CONTENT = """
<html>
<body>
    <p>Ho Ho Ho {name}!</p>
    <p>This email is from the Pollyanna (Secret Santa) Program.</p>
    <p>You drew the following names:<br>
    <span style="padding-left: 20px;">Genuine Gift: {gift_name}</span><br>
    <span style="padding-left: 20px;">Gag Gift: {gag_name}</span>
    </p>
    <p>Have fun shopping!</p>
    <p>P.S. Budgets for the gifts will be sent out at a later date.<br>
    Reach out if you received the same name twice.</p>
    {img_block}
</body>
</html>
"""