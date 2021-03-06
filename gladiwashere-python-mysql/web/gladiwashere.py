#
# Main program code for gladiwashere-python-mysql.
#
# Copyright (C) 2017 and later, Indie Computing Corp. All rights reserved. License: see package.
#

import cgi
import cgitb
import config
import mysql.connector
import sys

def doIt(environ) :
  cgitb.enable()

  try :
    db = mysql.connector.connect(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME)

  except mysql.connector.Error as err:
    print( 'ERROR: Cannot connect: {}'.format(err))
    return 'ERROR';

  if environ['REQUEST_METHOD'] == 'POST':
    # extract POST data into a form object
    post_env = environ.copy()
    post_env['QUERY_STRING'] = ''
    form = cgi.FieldStorage( fp=post_env['wsgi.input'], environ=post_env, keep_blank_values=True )

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO Comment( name, created, email, comment ) VALUES ( %s, NOW(), %s, %s );",
        ( form['name'].value, form['email'].value, form['comment'].value ))

    db.commit()
    cursor.close()

  cursor = db.cursor()
  cursor.execute("SELECT * FROM Comment ORDER BY id DESC LIMIT 10")

  ret = '''
<html>
 <head>
  <title>Glad-I-Was-Here Guestbook</title>
 </head>
 <body>
  <h1>Glad-I-Was-Here Guestbook</h1>
  <p>Example Python/MySQL app for <a href="http://ubos.net/">UBOS</a>.</p>
'''
  first = True
  for (id, created, name, email, comment) in cursor:
    if first:
      ret += "<h2>Comments:</h2>\n"
      ret += "<dl>\n"
    ret += " <dt>{} (on {})</dt>\n".format( name, created )
    ret += " <dd>{}</dd>\n".format( comment )
    first = False

  if not first:
    ret += "</dl>\n"

  cursor.close()
  db.close()

  ret += """
  <p>Please leave your comments here:</p>
  <form method="POST" action="{}">
   <table>
    <tr>
     <th>Name:</th>
     <td>
      <input type="text" name="name" size="40" maxlength="80" />
     </td>
    </tr>
    <tr>
     <th>E-mail:</th>
     <td>
      <input type="text" name="email" size="40" maxlength="80" />
     </td>
    </tr>
    <tr>
     <th>Comment:</th>
     <td>
      <textarea name="comment" maxlength="1024" cols="40" rows="8" ></textarea>
     </td>
    </tr>
    <tr>
     <td colspan="2" class="submit">
      <input type="submit" name="submit" value="Leave Comment" />
     </td>
   </table>
  </form>
 </body>
</html>
""".format( environ['SCRIPT_NAME'] )

  return [ ret.encode( 'utf-8' ) ]
