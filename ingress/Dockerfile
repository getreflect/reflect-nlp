## Build stage
FROM golang:alpine AS builder
ENV GO111MODULE=on

# Copy files to image
COPY . /app/src
WORKDIR /app/src

# Install Git
RUN apk add git ca-certificates

# Build image
RUN CGO_ENABLED=0 GOOS=linux go build -o /go/bin/app

## Image creation stage
FROM alpine:latest

# Copy user from build stage
COPY --from=builder /etc/passwd /etc/passwd

# Copy app
COPY --from=builder /go/bin/app /go/bin/app

# Expose ports
EXPOSE 8080

# Run app
CMD ["./go/bin/app"]