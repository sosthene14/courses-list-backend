from datetime import datetime


def validation_message_group(course_type="oracle", group_name=""):
  return f"""
<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>UNIPRO - Nouveau groupe ajouté</title>
         <style>
      body {{
        font-family: Arial, sans-serif;
        background-color: #f5f7fa;
        color: #333;
        margin-top: 100px;
        padding: 0;
      }}
      .container {{
        width: 100%;
        margin-top: 20px;
        max-width: 600px;
        margin: 0 auto;
        background-color: #fff;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        overflow: hidden;
      }}
      .header {{
        background-color: #10837f;
        color: #ffffff;
        text-align: center;
        padding: 20px;
      }}
      .header img {{
        width: 200px;
        height: auto;
      }}
      .content {{
        padding: 20px;
      }}
      .content h1 {{
        font-size: 24px;
        margin-bottom: 10px;
      }}
      .content p {{
        font-size: 16px;
        line-height: 1.5;
      }}
      .content .details {{
        margin: 20px 0;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 8px;
      }}
      .content .details p {{
        margin: 0;
        font-size: 14px;
        color: #555;
      }}
      .content .btn {{
        display: block;
        width: fit-content;
        margin: 0 auto;
        padding: 10px 20px;
        background-color: #171046;
        color: #ffffff;
        text-align: center;
        border-radius: 5px;
        text-decoration: none;
      }}
      .footer {{
        text-align: center;
        padding: 20px;
        background-color: #171046;
        color: #ffffff;
        font-size: 14px;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        UNIPRO
      </div>
      <div class="content">
        <p>Bonjour,</p>
        <p style="text-align: center;">
          Un nouveau groupe a été ajouté 
          cours : {course_type}
          groupe detail : {group_name}
      </div>
      <div class="footer">
        <p>Cordialement,</p>
        <p>L'équipe Rocolis</p>
      </div>
    </div>
  </body>
</html>

"""