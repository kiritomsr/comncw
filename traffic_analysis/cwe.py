from flask import Flask, request

app = Flask(__name__)

CONFIG_DATA = {
    'NAME': 'TestScoreLog',
    'PASSWORD': 'my_s3cr3t_p4ssw0rd'
}


# Process GET request
@app.route('/submit')
def log_score():
    input_coursework = request.args.get('coursework', '')
    input_student = request.args.get('student', '')
    input_score = request.args.get('score', '')
    USER_INPUT = {
        'coursework': input_coursework,
        'student': input_student,
        'score': input_score
    }
    print(input_coursework + input_student + input_score)
    response = "In {INPUT[coursework]}, {INPUT[student]} received mark of {INPUT[score]}".format(INPUT=USER_INPUT)  # Format output
    return ("[*] {CONFIG[NAME]} : " + response).format(CONFIG=CONFIG_DATA)
    # return format_response("[*] {CONFIG_DATA[NAME]} : " + response)


def format_response(log):
    return log.format(CONFIG_DATA=CONFIG_DATA)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
