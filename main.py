import boto3
import datetime
import redis
import yaml


cw = boto3.client('cloudwatch')


def cw_put_metric_data(name, value, host, db):
    cw.put_metric_data(Namespace='Sidekiq',
                       MetricData=[
                           {
                               'MetricName': name,
                               'Timestamp': datetime.datetime.now(),
                               'Value': value,
                               'Unit': 'Count',
                               'Dimensions': [
                                   {
                                       'Name': 'Host',
                                       'Value': host.split('.')[0]
                                   },
                                   {
                                       'Name': 'Database',
                                       'Value': str(db)
                                   },
                               ],
                           },
                       ])


def cw_put_metric_alarm(metric_name, cfg):
    host = cfg['host'].split('.')[0]

    alarm_name = '{}-{}'.format(host, metric_name)
    print('Setting up cloudwatch alarm for {}'.format(alarm_name))

    cw.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmDescription='Alarm for celery beat job {}'.format(metric_name),
        ActionsEnabled=False,
        MetricName=metric_name,
        Namespace='Sidekiq',
        Statistic='Maximum',
        Dimensions=[
            {
                'Name': 'Job',
                'Value': metric_name
            },
            {
                'Name': 'Host',
                'Value': host
            },
            {
                'Name': 'Database',
                'Value': str(cfg['db'])
            },
        ],
        Period=cfg['cw_period'],
        Unit='Count',
        EvaluationPeriods=cfg['cw_evaluation_periods'],
        Threshold=cfg['cw_threshold'],
        ComparisonOperator='GreaterThanThreshold',
        TreatMissingData='breaching',
    )


def handler(event, context):
    config = yaml.load(open('redis.yml'))

    for ns, cfg in config['sidekiq_namespaces'].items():
        port = cfg.get('port', 6379)
        db = cfg.get('db', 0)
        r = redis.StrictRedis(host=cfg['host'], port=port, db=db)
        queues = r.smembers(ns + ':queues')

        for q in queues:
            queue = q.decode('utf-8')
            queue_length = r.llen(ns + ':queue:' + queue)
            metric_name = '{}:{}'.format(ns, queue)
            print('host: {}, queue: {}, value: {}'.format(cfg['host'],
                                                          metric_name,
                                                          queue_length))
            cw_put_metric_data(metric_name, queue_length, cfg['host'], db)
            cw_put_metric_alarm(metric_name, cfg)
