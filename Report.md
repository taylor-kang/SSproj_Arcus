< SW스튜디오2 최종 실습 프로젝트 >
**Arcus를 통한 웹클라이언트 성능개선**
======================
* 멘토링 : 화요일  
* 2015004284 강태희  
* 2015004684 안건주  


## 1.  목표
---
네이버의 오픈소스 프로젝트인 Naver의 OSS(Open Source Software)인 Arcus(Memory Cache Cloud)를 사용해서 샘플 프로젝트에 구현해보고 Arcus 도입의 전/후 간의 성능을 비교한다.

## 2.  Docker Container List
---
Docker 컨테이너 리스트를 확인한다
<pre><code>$ docker ps</code></pre>
![Image](/image/docker ps.png)

> 1. ruo91/arcus -> arcus admin container  
> 2. ruo91/arcus-memcached -> arcus client container  
> 3. ruo91/arcus-memcached  
> 4. ruo91/arcus-memcached  
> 5. ngrinder/controller:3.4 -> ngrinder controller container  
> 6. ngrinder/agent:3.4 -> ngrinder agent container  
> 7. mysql:5.7 -> mysql container  
> 8. hyeongseok05/nbase-arc -> nbase-arc container  

### 2.1.  Arcus  
-------------
Arcus는 memcached와 ZooKeeper를 기반으로 네이버 (NAVER) 서비스들의 요구 사항을 반영해 개발한 메모리 캐시 클라우드이다. Arcus를 웹서버 또는 데이터베이스 사이에 위치시켜 빠른 응답 및 부하를 줄이기 위한 용도로 사용 할수 있다. Arcus에서 memcached를 확장해서 지원하는 추가 기능 중 ZooKeeper 기반의 cache cloud 관리, Collection 자료구조 (List), B+tree을 중점적으로 사용하여 프로젝트를 진행하였다.  

Arucs는 Docker Hub의 ruo91/arcus를 가져와 설치하였다.
#### 2.1.1. arcus-admin   
zookeeper로 운영되는 arcus-memcached 서버  
<pre><code>$ docker run -d --name="arcus-admin" -h "arcus" ruo91/arcus</code></pre>

#### 2.1.2. arcus-memcached1/2/3   
zookeeper로 운영되는 arcus-memcached 클라이언트 3개  
<pre><code>$ docker run -d --name="arcus-memcached-1" -h "memcached-1" ruo91/arcus:memcached
$ docker run -d --name="arcus-memcached-2" -h "memcached-2" ruo91/arcus:memcached
$ docker run -d --name="arcus-memcached-3" -h "memcached-3" ruo91/arcus:memcached</code></pre>  

Arcus에서 관리하는 memcached가 온라인 상태에 있고 zookeeper_list에서 admin을 포함한 memcached 4개가 관리되고 있음을 알수있다.

> ![Image](/image/zookeeper_list.png)

  
### 2.2.  Mysql
-------------
<pre><code> $ docker run -d \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=test \
  --name mysql \
  mysql:5.7</code></pre>  
대표적인 관계형 데이터베이스 

### 2.3.  Arcus Web Application – 부탁한양 
-------------
<pre><code> $ docker run -p 8080:80 \
  --link mysql:mysql_host \
  -e DATABASE_HOST=mysql_host \
  -e DATABASE_USER=root \
  -e DATABASE_PASS=root \
  -e DATABASE_NAME=test \
  --name askhy \
  askhy</code></pre>
  
askhy(부탁한양) https://github.com/Prev/askhy : open source 활용
Flask기반 웹클라이언트 
arcus 와 연동
mysql DB와 연동

### 2.4.  nGrinder
-------------
nGrinder는 네이버의 성능측정 오픈소스이다. 
mysql, nbase-arc, arcus-memcached 의 성능 측정을 위해 ngrinder 를 사용했다. 

#### 2.4.1. nGrinder – controller 
성능 테스트를 위한 웹 인터페이스, 테스트 프로세스를 조정 및 대조, 표시 통계 테스트를 할 수 있는 기능을 제공한다.  
<pre><code>$ docker run -d -v ~/ngrinder-controller:/opt/ngrinder-controller -p 80:80 -p 16001:16001 -p 12000-12009:12000-12009 ngrinder/controller:3.4</code></pre>


#### 2.4.1. nGrinder – agent    
Controller의 명령을 받아 실행에 옮긴다.
<pre><code>$ docker run -v ~/ngrinder-agent:/opt/ngrinder-agent -d ngrinder/agent:3.4 172.17.0.6:80</code></pre>


### 2.5.  nBase - ARC
-------------
서버 한대로 처리할 수 없는 대규모 서비스의 경우 분산 시스템이 필요하다. nBASE-ARC의 경우 이러한 서비스를 처리하기 위한 플랫폼으로 Redis가 제공하는 고성능 DB의 장점을 지닌 서비스 중단 없이 장비를 추가할 수 있는 확장성을 지닌 클러스터이다. Redis API를 그대로 활용할 수 있기 때문에 이를 활용하여 테스트 및 모니터링을 수행하였다.  
nBase-ARC는 Docker Hub의 hyeongseok05/nbase-arc를 가져와 설치하였다.
<pre><code>$ docker run -p 6000:6000 -d --name=test hyeongseok05/nbase-arc</code></pre> 

## 3. nGrinder를 통한 Stress test
---
엄밀한 환경을 만들어 놓고 사용한 것이 아니라 결과는 크게 신뢰할 수 없지만, mysql 만 사용할 때보다 arcus-memcached, nbase-arc 를 캐시로 사용하면 향상된 TPS 를 보여주었다. localhost:8080에 접속하여 agent를 다운 받아 run-agent 스크립트를 실행하면 준비가 끝난다.결과는 아래와 같다.  
### 3.1.  MySQL Stress test  
-------------
MySQL만 사용하여 쿼리하는 페이지(대조군)는 최고 TPS가 3.2로 나타났다.
> ![Image](/image/mysql_stress.png)  

### 3.2.  MySQL + Arcus 도입 후 Stress test 
-------------
Arcus를 MySQL의 캐시로 사용하는 페이지는 최고 TPS가 4.3으로 나타났다. 약 34%의 성능 향상을 보여주었으며, 테스트 처음 캐시가 비었을 때는 낮았던 성능이 점차로 증가하여 안정화되는 모습을 볼 수 있다.
(캐시된 데이터의 성능과 캐시되지 않은 일반 상황의 성능비교, TPS 성능비교, 캐시로 인한 DBMS 트래픽 감소정도) 
> ![Image](/image/arcus_stress.png)  

### 3.3.  MySQL + nBase-ARC 도입 후 Stress test 
-------------
nBase-ARC를 캐시로 사용하는 페이지는 최고 TPS가 %으로 나타났다. 약 %%%의 성능 향상으로 Arcus보다는 낮지만 여전히 뚜렷한 수치를 나타내었다. 마찬가지로 처음에 낮았던 성능이 얼마 후 안정화되는 모습을 보여준다.
> ![Image](/image/.png)  

## 4. Open Source Contribution
---

## 5. 사용한 Open Source License  
---
* arcus
* ngrinder
* docker
* mysql
* prev/askhy 

## 6. 결론 
---

## 7. 역할분담
---
