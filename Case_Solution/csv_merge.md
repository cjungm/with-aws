S3에 3개 Folder에 schema가 같은 csv 파일이 여려개가 존재한다.
3개 folder의 모든 csv를 1개의 파일로 변환하기

제약사항)

1. EC2는 t2.micro보다 낮은 사양으로 만들 것
2. 각 폴더의 파일 갯수를 셀 수 있는 py 코드 짜기

[Solution](Solution/sol_csv_merge.md)