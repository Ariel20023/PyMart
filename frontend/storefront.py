import os
import time
import requests
import streamlit as st

st.set_page_config(page_title="PyMart Store", layout="wide")


CATALOG_API_URL = os.getenv("CATALOG_API_URL","http://catalog_service:8000")

AUTH_API_URL = os.getenv("AUTH_API_URL","http://auth_service:8001")

#האם login קיים כבר בזיכרון?
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "role" not in st.session_state:
    st.session_state.role = None

if "token" not in st.session_state:
    st.session_state.token = None

if "just_logged_out" not in st.session_state:
    st.session_state.just_logged_out = False

#לוקח פרמטרים מה url 
params = st.query_params
#שומר את הפרטים
saved_token = params.get("token")
saved_username = params.get("username")
saved_role = params.get("role")

#007
if (
    not st.session_state.logged_in
    and not st.session_state.just_logged_out
    and saved_token
):
    st.session_state.logged_in = True
    st.session_state.username = saved_username
    st.session_state.role = saved_role
    st.session_state.token = saved_token

# מחזיר "Authorization": "Bearer abc123"  
def auth_headers():

    return {
        "Authorization":
        f"Bearer {st.session_state.token}"
    }


def load_products():

    response = requests.get(
        f"{CATALOG_API_URL}/products"
    )

    response.raise_for_status()

    return response.json() #return json of products


st.title("PyMart Store")

st.sidebar.title("משתמש")


if not st.session_state.logged_in: #רק אם המששתמש לא מחובר 

    auth_tab1, auth_tab2 = st.sidebar.tabs(
        ["Login", "Register"]
    )

    with auth_tab1:

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",#מסתיר את הסיסמה
            key="login_password"
        )

        if st.button("Login"):

            response = requests.post(
                f"{AUTH_API_URL}/login",
                json={
                    "email": login_email,
                    "password": login_password
                }
            )

            if response.status_code == 200:

                data = response.json() #return name token and role 

                st.session_state.logged_in = True
                st.session_state.username = data["username"]
                st.session_state.role = data["role"]
                st.session_state.token = data["token"]
                st.session_state.just_logged_out = False

                st.query_params["token"] = data["token"] #save token
                st.query_params["username"] = data["username"]
                st.query_params["role"] = data["role"]

                time.sleep(0.2)

                st.rerun() #מריץ את הפרונטד בתור מחובר 

            else:

                st.error(
                    "שם משתמש או סיסמה לא נכונים"
                )

    with auth_tab2:

        register_username = st.text_input(
            "Username",
            key="register_username"
        )

        register_email = st.text_input(
            "Email",
            key="register_email"
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        register_shipping_address = st.text_input(
            "Shipping Address",
            key="register_shipping_address"
        )

        if st.button("Register"):

            response = requests.post(
                f"{AUTH_API_URL}/register",
                json={
                    "username": register_username,
                    "email": register_email,
                    "password": register_password,
                    "shipping_address": register_shipping_address
                }
            )

            if response.status_code == 200:

                st.success(
                    "המשתמש נוצר בהצלחה"
                )

            else:

                st.error(response.text)

else:

    st.sidebar.success(   #מציג בצד 
        f"מחובר: {st.session_state.username}"
    )

    st.sidebar.write(  #מציג תפקיד 
        f"תפקיד: {st.session_state.role}"
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.token = None
        st.session_state.just_logged_out = True

        st.query_params.clear()

        time.sleep(0.2)

        st.rerun()#מריץ מחדש את כל הפרונט


if st.session_state.role == "admin":

    tab1, tab2, tab3 = st.tabs(
        [
            "חנות מוצרים",
            "הוספת מוצר",
            "ניהול מוצרים"
        ]
    )

else:

    tab1 = st.tabs(
        [
            "חנות מוצרים"
        ]
    )[0]


with tab1:

    st.header("כל המוצרים")

    try:

        products = load_products()#מנסה לטעון את המוצרים 

    except Exception as e:

        st.error(
            f"שגיאה בטעינת מוצרים: {e}"
        )

        st.stop()

    if not products:

        st.info("אין מוצרים להצגה")

    else:

        cols = st.columns(3)#יוצר 3 עמודות לתצוגה 

        for index, product in enumerate(products):

            with cols[index % 3]:#מחלק את המוצרים בין 3 עמודות
                st.subheader(product["name"])

                if product.get("image_url"):#בודק  אם יש תמונה 

                    st.image( #מושך את התמונה מה minio
                        product["image_url"],
                        use_container_width=True
                    )

                else:

                    st.info("אין תמונה")

                st.write(product["description"])

                st.write(
                    f"קטגוריה: {product['category']}"
                )

                st.write(
                    f"מחיר: ${product['price']}"
                )

                st.write(
                    f"מלאי: {product['stock_count']}"
                )

                st.caption(
                    f"ID: {product['id']}"
                )


if st.session_state.role == "admin": #רק אדמין יכול לשנות מוצרים

    with tab2:

        st.header("הוספת מוצר חדש")

        name = st.text_input(#שם מוצר
            "שם מוצר",
            key="add_name"
        )

        description = st.text_area(
            "תיאור",
            key="add_description"
        )

        price = st.number_input(
            "מחיר",
            min_value=0.01,
            step=0.5,
            key="add_price"
        )

        category = st.text_input(
            "קטגוריה",
            key="add_category"
        )

        stock_count = st.number_input(
            "מלאי",
            min_value=0,
            step=1,#כל לחיצה מורידה 1
            key="add_stock"#מזהה יחודי בסטרימליט
        )

        image = st.file_uploader(
            "בחר תמונה",
            type=["jpg", "jpeg", "png", "webp"],
            key="add_image"
        )

        if st.button(
            "הוסף מוצר",
            key="add_product"
        ):

            data = {
                "name": name,
                "description": description,
                "price": price,
                "category": category,
                "stock_count": stock_count
            }

            files = None #בהתחלה אין קובץ 

            if image:

                files = { #מכין תמונה לשליחה ב http
                    "image": (
                        image.name,
                        image.getvalue(),#מחזיר קובץ בביטים
                        image.type
                    )
                }

            response = requests.post( #שולח לקטלוג
                f"{CATALOG_API_URL}/products",
                data=data,
                files=files,
                headers=auth_headers()
            )

            if response.status_code == 200:

                st.success("המוצר נוסף בהצלחה")

                time.sleep(0.5)

                st.rerun()

            else:

                st.error(response.text)

    with tab3:

        st.header("ניהול מוצרים")

        products = load_products()

        if not products:

            st.info("אין מוצרים")

        else:

            for product in products:

                st.divider()#קו הפרדה בין המוצרים

                st.subheader(product["name"])#שם המוצר

                if product.get("image_url"):#תמונה

                    st.image(
                        product["image_url"],
                        width=200
                    )

                new_name = st.text_input(
                    "שם מוצר",
                    value=product["name"],
                    key=f"name_{product['id']}"
                )

                new_description = st.text_area(#נותן אזור לכתיבה
                    "תיאור",
                    value=product["description"],
                    key=f"description_{product['id']}"#נותן מזהה יחודי 
                )

                new_price = st.number_input(
                    "מחיר",
                    min_value=0.01,
                    value=float(product["price"]),
                    key=f"price_{product['id']}"
                )

                new_category = st.text_input(
                    "קטגוריה",
                    value=product["category"],
                    key=f"category_{product['id']}"
                )

                new_stock = st.number_input(
                    "מלאי",
                    min_value=0,
                    value=int(product["stock_count"]),
                    step=1,
                    key=f"stock_{product['id']}"
                )

                new_image = st.file_uploader(
                    "החלף תמונה",
                    type=["jpg", "jpeg", "png", "webp"],
                    key=f"image_{product['id']}"
                )

                col1, col2 = st.columns(2)#יוצר 2 עמודות לעדכון ומחיקה

                with col1:

                    if st.button(
                        "עדכן מוצר",
                        key=f"update_{product['id']}"
                    ):

                        update_data = { #מילון עם הערכים החדשים 
                            "name": new_name,
                            "description": new_description,
                            "price": new_price,
                            "category": new_category,
                            "stock_count": new_stock,
                            "image_url": product.get("image_url")
                        }

                        response = requests.put(
                            f"{CATALOG_API_URL}/products/{product['id']}",
                            json=update_data,
                            headers=auth_headers()#מחזיר את התוקן של המשתמש
                        )

                        if response.status_code != 200:

                            st.error(response.text)

                            st.stop()

                        if new_image:#אם בחר תמונה חדשה

                            files = {
                                "image": (
                                    new_image.name,
                                    new_image.getvalue(),
                                    new_image.type
                                )
                            }

                            image_response = requests.post(
                                f"{CATALOG_API_URL}/products/{product['id']}/image",
                                files=files,
                                headers=auth_headers()
                            )

                            if image_response.status_code != 200:

                                st.error(
                                    image_response.text
                                )

                                st.stop()

                        st.success("המוצר עודכן")

                        time.sleep(0.5)

                        st.rerun()

                with col2:

                    if st.button(
                        "מחק מוצר",
                        key=f"delete_{product['id']}"
                    ):

                        response = requests.delete(
                            f"{CATALOG_API_URL}/products/{product['id']}",
                            headers=auth_headers()
                        )

                        if response.status_code == 200:

                            st.success("המוצר נמחק")

                            time.sleep(0.5)

                            st.rerun()

                        else:

                            st.error(response.text)