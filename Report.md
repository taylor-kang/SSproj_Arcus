< SW스튜디오2 최종 실습 프로젝트 >
**Arcus를 통한 웹클라이언트 성능개선**
======================
* 멘토링 : 화요일  
* 2015004284 강태희  
* 2015004684 안건주  

# 1.  목표 
네이버의 오픈소스 프로젝트인 Naver의 OSS(Open Source Software)인 Arcus(Memory Cache Cloud)를 사용해서 샘플 프로젝트에 구현해보고 Arcus 도입의 전/후 간의 성능을 비교한다.

# 2.  Docker Container List
## 2.1 Arcus
* arcus-admin   
zookeeper로 운영되는 arcus-memcached 서버  
<pre><code>$ docker run -d --name="arcus-admin" -h "arcus" ruo91/arcus</code></pre>

* arcus-memcached1/2/3   
zookeeper로 운영되는 arcus-memcached 클라이언트 3개  
<pre><code>$ docker run -d --name="arcus-memcached-1" -h "memcached-1" ruo91/arcus:memcached
$ docker run -d --name="arcus-memcached-2" -h "memcached-2" ruo91/arcus:memcached
$ docker run -d --name="arcus-memcached-3" -h "memcached-3" ruo91/arcus:memcached</code></pre>  

  
## 2.2 Mysql
대표적인 관계형 데이터베이스 

## 2.3 Arcus Web Application – 부탁한양 
askhy(부탁한양) https://github.com/Prev/askhy : open source 활용
Flask기반 웹클라이언트 
arcus 와 연동 
mysql DB와 연동 

## 2.4 nGrinder
nGrinder는 네이버의 성능측정 오픈소스이다.   

* nGrinder – controller   
성능 테스트를 위한 웹 인터페이스, 테스트 프로세스를 조정 및 대조, 표시 통계 테스트를 할 수 있는 기능을 제공한다.  
<pre><code>$ docker run -d -v ~/ngrinder-controller:/opt/ngrinder-controller -p 80:80 -p 16001:16001 -p 12000-12009:12000-12009 ngrinder/controller:3.4</code></pre>


* nGrinder – agent    
Controller의 명령을 받아 실행에 옮긴다.
<pre><code>$ docker run -v ~/ngrinder-agent:/opt/ngrinder-agent -d ngrinder/agent:3.4 172.17.0.6:80</code></pre>


## 2.5 nBase - ARC
서버 한대로 처리할 수 없는 대규모 서비스의 경우 분산 시스템이 필요하다. nBASE-ARC의 경우 이러한 서비스를 처리하기 위한 플랫폼으로 Redis가 제공하는 고성능 DB의 장점을 지닌 서비스 중단 없이 장비를 추가할 수 있는 확장성을 지닌 클러스터이다. Redis API를 그대로 활용할 수 있기 때문에 이를 활용하여 테스트 및 모니터링을 수행하였다.

# 3. nGrinder를 통한 Stress test
* Arcus 도입 전 Stress test

* Arcus 도입 후 Stress test 
(캐시된 데이터의 성능과 캐시되지 않은 일반 상황의 성능비교, TPS 성능비교, 캐시로 인한 DBMS 트래픽 감소정도) 

# 4. Open Source Contribution 

# 5. 사용한 Open Source License
* arcus
* ngrinder
* docker
* mysql
* prev/askhy 

# 6. 결론 

# 7. 역할분담
