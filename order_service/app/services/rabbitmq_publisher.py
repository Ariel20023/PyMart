import json
import os

import pika #לעבוד עם rabbitmq


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST","rabbitmq")

ORDER_EVENTS_QUEUE = "order_events"#שם התור 


def publish_order_placed_event(order_data: dict):#שולח event לראביט 

    connection = pika.BlockingConnection(#יוצר חיבור לתור
        pika.ConnectionParameters(#הגדרות 
            host=RABBITMQ_HOST
        )
    )

    channel = connection.channel()#ערוץ ישיר מול המסד

    channel.queue_declare(#יוצר תור אם לא קיים
        queue=ORDER_EVENTS_QUEUE,
        durable=True#שלא ימחק אחרי restart
    )

    event = {
        "event": "order.placed",
        "data": order_data
    }

    channel.basic_publish(#שליחת המיידע
        exchange="",#שולחים ישירות לתור
        routing_key=ORDER_EVENTS_QUEUE,
        body=json.dumps(event),#כדי שישלח בביטים ולא dict
        properties=pika.BasicProperties(
            delivery_mode=2#שומר את ההודעה בדיסק ולכן זה 2 כדי שגם אם ריסטרט לא נופל
        )
    )

    connection.close()