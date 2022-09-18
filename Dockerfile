FROM registry.gitlab.com/sss-ai-group/sss-fashion-be/sss-prebuilt-image/recsys-prebuilt-image:main-prebuilt

# set locale
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV TZ=Asia/Ho_Chi_Minh

COPY . /ai_server
WORKDIR /ai_server
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]