S3에 하단과 같이 작성된 텍스트 파일이 있다.

```
이것은 Endpoint test 용 text 입니다.
이것은 Endpoint 실전용 text 입니다.
이것은 Endpoint test 용 text 입니다.
이것은 Endpoint 실전용 text 입니다.
```

이 파일에서 특정 단어가 들어간 Line을 제거한 파일 생성 후 S3에 업로드 하기

권장 방법) s3fs, unix/linux cmd만 사용하여 S3 Download 및 Upload 진행

제약 사항) 

1. PC에서 직접 Download 후 삭제 금지
2. AWS CLI(SDK) 사용 파일 Download 금지
3. Pandas 사용금지

[Solution](Solution/sol_s3fs&bash_script.md)