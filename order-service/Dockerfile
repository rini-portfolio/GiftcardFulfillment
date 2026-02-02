# multi-stage Dockerfile for order-service
FROM maven:3.9.4-eclipse-temurin-21 as build
WORKDIR /workspace
COPY pom.xml ./
COPY src ./src
RUN mvn -B -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /workspace/target/*.jar /app/app.jar
ENV JAVA_OPTS=""
EXPOSE 8080
ENTRYPOINT ["sh","-lc","java $JAVA_OPTS -jar /app/app.jar"]