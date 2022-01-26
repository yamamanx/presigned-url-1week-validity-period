# presigned-url-1week-validity-period
IAMロールでは署名付きURLを1週間有効にできないのでIAMユーザーのアクセスキーをパラメータストアから取得して生成する

パラメータストアは以下で作成してますので、適宜読み替えてください。

- /presinedurl/accesskey, SecureString, アクセスキーID
- /presinedurl/secretaccesskey, SecureString, シークレットアクセスキー
- /private/private-notification, String, SNSトピックのARN
