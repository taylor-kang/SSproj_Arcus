< SW스튜디오2 최종 실습 프로젝트 >
**Arcus와 nBase-ARC를 통한 웹클라이언트 성능개선**
======================
* 멘토링 : 화요일  
* 2015004284 강태희  
* 2015004684 안건주  

<br /><br/>

## 1.  목표
---
네이버의 오픈소스 프로젝트인 Naver의 OSS(Open Source Software)인 Arcus(Memory Cache Cloud)를 사용해서 샘플 프로젝트에 구현해보고 Arcus 도입의 전/후 간의 성능을 비교한다.

<br /><br/>
<br /><br/>

## 2.  Docker Container List
---
Docker 컨테이너 리스트를 확인해보면 프로젝트 실행을 위한 가지 컨테이너가 실행되고 있음을 볼수 있다.
<pre><code>$ docker ps</code></pre>
>![Image](/image/docker ps.png)

> 1. ruo91/arcus -> arcus admin container  
> 2. ruo91/arcus-memcached -> arcus client container  
> 3. ruo91/arcus-memcached  
> 4. ruo91/arcus-memcached  
> 5. ngrinder/controller:3.4 -> ngrinder controller container  
> 6. ngrinder/agent:3.4 -> ngrinder agent container  
> 7. mysql:5.7 -> mysql container  
> 8. hyeongseok05/nbase-arc -> nbase-arc container  

<br /><br/>

### 2.1.  Arcus  
-------------
Arcus는 memcached와 ZooKeeper를 기반으로 네이버 (NAVER) 서비스들의 요구 사항을 반영해 개발한 메모리 캐시 클라우드이다. Arcus를 웹서버 또는 데이터베이스 사이에 위치시켜 빠른 응답 및 부하를 줄이기 위한 용도로 사용 할수 있다. Arcus에서 memcached를 확장해서 지원하는 추가 기능 중 ZooKeeper 기반의 cache cloud 관리, Collection 자료구조 (List), B+tree을 중점적으로 사용하여 프로젝트를 진행하였다.  
Arucs는 Docker Hub의 [ruo91/arcus](https://hub.docker.com/r/ruo91/arcus/)를 가져와 port번호 2181에 연결하여 설치하였다.  

<br /><br/>

다음 사진에서 Arcus에서 관리하는 memcached가 온라인 상태에 있고 zookeeper_list에서 admin을 포함한 memcached 4개가 관리되고 있음을 알수있다.
> ![Image](/image/zookeeper_list.png)

<br /><br/>

> #### 2.1.1. arcus-admin   
zookeeper로 운영되는 arcus-memcached 서버  

```bash
$ docker run -d --name="arcus-admin" -h "arcus" ruo91/arcus
```


> #### 2.1.2. arcus-memcached1/2/3   
zookeeper로 운영되는 arcus-memcached 클라이언트 3개  

```bash
$ docker run -d --name="arcus-memcached-1" -h "memcached-1" ruo91/arcus:memcached
$ docker run -d --name="arcus-memcached-2" -h "memcached-2" ruo91/arcus:memcached
$ docker run -d --name="arcus-memcached-3" -h "memcached-3" ruo91/arcus:memcached
```

<br /><br/>

### 2.2.  Mysql
-------------
웹클라이언트 데이터베이스 관리를 위하여 대표적인 관계형 데이터베이스인  Mysql을 사용하였다.웹클라이언트에서는 DB와의 호환을 위하여 오픈소스 PyMysql을 사용하였다. 

```bash
$ docker run -d \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=test \
  --name mysql \
  mysql:5.7
```

Mysql을 port번호 3306에 연결하였다.

<br /><br/>

### 2.3.  nBase - ARC
-------------
서버 한대로 처리할 수 없는 대규모 서비스의 경우 분산 시스템이 필요하다. nBASE-ARC의 경우 이러한 서비스를 처리하기 위한 플랫폼으로 Redis가 제공하는 고성능 DB의 장점을 지닌 서비스 중단 없이 장비를 추가할 수 있는 확장성을 지닌 클러스터이다. Redis API를 그대로 활용할 수 있기 때문에 이를 활용하여 테스트 및 모니터링을 수행하였다.  
nBase-ARC는 Docker Hub의 hyeongseok05/nbase-arc를 가져와 설치하였다.
<pre><code>$ docker run -p 6000:6000 -d --name=test hyeongseok05/nbase-arc</code></pre> 

nBase - ARC를 port번호 6000에 연결하였다.

<br /><br/>


### 2.4.  nGrinder
-------------
nGrinder는 네이버의 성능측정 오픈소스이다. 
mysql, nbase-arc, arcus-memcached 의 성능 측정을 위해 ngrinder 를 사용했다. 
nGrinder를 port번호 8000에 연결하였다.

<br /><br/>

> #### 2.4.1. nGrinder – controller 
성능 테스트를 위한 웹 인터페이스, 테스트 프로세스를 조정 및 대조, 표시 통계 테스트를 할 수 있는 기능을 제공한다.  
<pre><code>$ docker run -d -v ~/ngrinder-controller:/opt/ngrinder-controller -p 80:80 -p 16001:16001 -p 12000-12009:12000-12009 ngrinder/controller:3.4</code></pre>


> #### 2.4.1. nGrinder – agent    
Controller의 명령을 받아 실행에 옮긴다.
<pre><code>$ docker run -v ~/ngrinder-agent:/opt/ngrinder-agent -d ngrinder/agent:3.4 172.17.0.6:80</code></pre>

<br /><br/>


### 2.5.  Web Application – 부탁한양 
-------------
[askhy(부탁한양)](https://github.com/Prev/askhy) open source 활용하였고 port번호 80에 연결하였다.
Flask기반 웹클라이언트로 arcus, mysql DB 와 연동하였다.

<pre><code> $ docker run -p 8080:80 \
  --link mysql:mysql_host \
  -e DATABASE_HOST=mysql_host \
  -e DATABASE_USER=root \
  -e DATABASE_PASS=root \
  -e DATABASE_NAME=test \
  --name askhy \
  askhy</code></pre>

<br /><br/>

> #### 2.5.1. arcus를 통한 성능개선 
웹페이지 메인화면에 출력되는 ask data를 arcus를 통해 캐싱하였다. 처음 데이터 접근시에는 데이터를 캐싱하고 이후 데이터를 접근할때는 arcus 캐시에서 가져오므로 성능을 개선시킬수 있었다. 
[arcus-python-client](https://github.com/naver/arcus-python-client)에 `test.py`코드를 참고하여 list type의 자료형을 관리하는 방법을 찾았다. 


```bash
docker run -p 8080:80 \
  --link mysql:mysql_host \
  -e DATABASE_HOST=mysql_host \
  -e DATABASE_USER=root \
  -e DATABASE_PASS=root \
  -e DATABASE_NAME=test \
  -e ARCUS_URL=172.17.0.4:2181 \
  -e ARCUS_SERVICE_CODE=ruo91-cloud \
  --name askhy \
  askhy
```


~~~python
#####################################################################################################
#
# TEST 2: list
#
#####################################################################################################
ret = client.lop_create('test:list_1', ArcusTranscoder.FLAG_STRING, timeout)
print(ret.get_result())
assert ret.get_result() == True

items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5', 'item 6']

for item in items:
	ret = client.lop_insert('test:list_1', -1, item)
	print(ret.get_result())
	assert ret.get_result() == True

ret = client.lop_get('test:list_1', (0, -1))
print(ret.get_result())
assert ret.get_result() == items

ret = client.lop_get('test:list_1', (2, 4))
print(ret.get_result())
assert ret.get_result() == items[2:4+1]

ret = client.lop_get('test:list_1', (1, -2))
print(ret.get_result())
assert ret.get_result() == items[1:-2+1]

~~~

<br />

적용시킨 주요 코드 부분이다. `cursor.execute("SELECT *, (SELECT COUNT(*) FROM cheer WHERE ask_id = ask.id) AS cheer_cnt FROM ask”)`이 SQL문을 캐시한 것이다.
```python
success = True
	cache = client.lop_get('askhy:asktable_',(0, -1)).get_result()

	if not cache :
		success = False

	else :
		result = []

		from datetime import datetime

		for row in cache :
			item = row.split("/")
			result.append((
				int(item[0]), # id
				item[1], # message
				item[2], # ip_address
				datetime.strptime(item[3], '%Y-%m-%d %H:%M:%S'), # register_time
				int(item[4]), # cheer_cnt
			))

	if not success :
		cache = []

		with get_db().cursor() as cursor :
			ret = client.lop_create('askhy:asktable_', ArcusTranscoder.FLAG_STRING, timeout)
			
			cursor.execute("SELECT *, (SELECT COUNT(*) FROM `cheer` WHERE ask_id = ask.id) AS cheer_cnt FROM `ask`")
			
			result = cursor.fetchall()
			
			for item in result:
				#print(item)

				data = "%s/%s/%s/%s/%s" % (
					str(item[0]), # id
					item[1], # message
					item[2], # ip_address
					item[3].strftime("%Y-%m-%d %H:%M:%S"), # register_time
					str(item[4]), # cheer_cnt
				)

				
				finish = client.lop_insert('askhy:asktable_', -1, data)

```
<br /><br/>

> #### 2.5.2. nBase-arc를 통한 성능개선  

```bash
docker run -p 8080:80 \
  --link mysql:mysql_host \
  -e DATABASE_HOST=mysql_host \
  -e DATABASE_USER=root \
  -e DATABASE_PASS=root \
  -e DATABASE_NAME=askhy \
  -e REDIS_HOST=172.17.0.9 \
  -e REDIS_PORT=6000 \
  --name askhy \
  askhy
```
  
<br /><br/>

nBase의 경우 redis와 호환이 되기 때문에 단지 redis 사용하는 코드를 nBase로 연결 시켜 개선하였다. 적용시킨 주요 코드 부분이다. redis에서 사용하는 `lrange()`함수와 `lpush()`함수가 그대로 사용되었음을 볼 수 있다.


```python
cache = client.lrange('askhy:asktable_', 0, -1)


	if not cache :
		success = False

	else :

		result = []

		from datetime import datetime

		for row in cache :
			item = row.decode().split("/")
			result.append((
				int(item[0]), # id
				item[1], # message
				item[2], # ip_address
				datetime.strptime(item[3], '%Y-%m-%d %H:%M:%S'), # register_time
				int(item[4]), # cheer_cnt
			))

	if not success :
		cache = []

		with get_db().cursor() as cursor :
			
			cursor.execute("SELECT *, (SELECT COUNT(*) FROM `cheer` WHERE ask_id = ask.id) AS cheer_cnt FROM `ask`")
			
			result = cursor.fetchall()
			
			for item in result:
				#print(item)

				data = "%s/%s/%s/%s/%s" % (
					str(item[0]), # id
					item[1], # message
					item[2], # ip_address
					item[3].strftime("%Y-%m-%d %H:%M:%S"), # register_time
					str(item[4]), # cheer_cnt
				)

				finish = client.lpush('askhy:asktable_', data)
				
```
<br /><br/>
<br /><br/>

## 3. nGrinder를 통한 Stress test
---
엄밀한 환경을 만들어 놓고 사용한 것이 아니라 결과는 크게 신뢰할 수 없지만, mysql 만 사용할 때보다 arcus-memcached, nbase-arc 를 캐시로 사용하면 향상된 TPS 를 보여주었다. localhost:8080에 접속하여 agent를 다운 받아 run-agent 스크립트를 실행하면 준비가 끝난다.  
데이터 베이스에 존재하는 데이터(레코드)는 약 5000개이며, 5000개의 데이터를 입출력하는 것에 cache를 두었었다.
결과는 아래와 같다.  

<br /><br/>

> ### 3.1.  MySQL Stress test  
-------------
MySQL만 사용하여 쿼리하는 페이지는 평균 TPS가 2.9로 나타났다.
![Image](/image/mysql_stress.png)  

> ### 3.2.  MySQL + Arcus 도입 후 Stress test 
-------------
Arcus를 MySQL의 캐시로 사용하는 페이지는 평균 TPS가 4.3으로 나타났다. 약 48%의 성능 향상을 보여주었으며, 테스트 처음 캐시가 비었을 때는 낮았던 성능이 점차로 증가하여 안정화되는 모습을 볼 수 있다.
(캐시된 데이터의 성능과 캐시되지 않은 일반 상황의 성능비교, TPS 성능비교, 캐시로 인한 DBMS 트래픽 감소정도) 
![Image](/image/arcus_stress.png)  

> ### 3.3.  MySQL + nBase-ARC 도입 후 Stress test 
-------------
nBase-ARC를 캐시로 사용하는 페이지는 평균 TPS가 3.3으로 나타났다. 약 13%의 성능 향상으로 Arcus보다는 낮지만 여전히 뚜렷한 수치를 나타내었다. 마찬가지로 처음에 낮았던 성능이 얼마 후 안정화되는 모습을 보여준다.
![Image](/image/nbase_stress.png)  

<br />
성능 비교가 명시적으로 나타나지 않은 이유는 html data 길이 자체가 길어져서 data를 다운로드 받고 처리하는 양이 커졌기 때문으로 사료된다.
<br/>
<br /><br/>

## 4. Open Source Contribution
---
https://github.com/naver/arcus-python-client/pulls 에 typo fix를 요청하였습니다. (ahngj96 : 안건주, rkdxogml5768 : 강태희)
![Image](/image/contribution.png)  

<br /><br/>
<br /><br/>

## 5. 사용한 Open Source License  
---
* arcus - [Apache 2.0 License](link)
* ngrinder - [Apache 2.0 License](link)
* docker - [Apache 2.0 License](link)
* PyMySQL - [MIT License](link)
* prev/askhy - [MIT License](link)
* mysql 

<br /><br/>
<br /><br/>

## 6. 프로젝트 진행 과정
---

<br />

> ### 6.1.  Verification  
프로그래밍 전략으로 Pair Programming을 채택하여 프로젝트를 진행하였다. 이 과정에서 자연스럽게 오류를 발견하고 개선할 수 있었다. 
구현을 마친 후 Fagan이 제시한 Software Inspection Process을 따라서 해보았다. 

- Planning  
 크리에이티브 소프트웨어 랩실을 빌려 코드 검사 계획을 세웠다.

- Overveiw, Individual preparation  
 Pair programming을 했으므로 이 과정을 생략하였다.

- Inspection meeting  
코드를 줄 단위로 유심히 읽어내려 가면서 오류를 찾았다. 페어프로그래밍 당시에 서로 찾아준 오류들이 많아 이 과정에서 오류는 발견되지 않았다.

- Rework, Follow-up  
이 과정에서 오류가 발견되지 않아 변경하지 않았다.

<br />

> ### 6.2.  Validation  
테스트는 Integration Testing 방식을 채택했다. 구현을 마친 후에 bottom-up 방식으로 Integration Testing하였다. Test code를 따로 준비하지 않고 python 코드 내부에서 5000개의 데이터를 생성하여 테스트 하였다.

- MySQL 컨테이너와 APP 컨테이너간의 통신
- MySQL 컨테이너와 APP 컨테이너, Arcus간의 통신
- MySQL 컨테이너와 APP 컨테이너, nBase간의 통신

위 세 가지를 순서대로 추가하면서 테스트를 해보았다. `/`가 메세지에 포함되면 작동이 되지 않는 문제가 발생하는데, 그 문제는 예상범위 안의 문제이며, 따로 예외처리를 해줄 것이다.

<br /><br/>
<br /><br/>


## 7. 결론
---
웹 어플리케이션 제작 프로젝트를 진행해본 적이 없어 많은 시행착오를 겪었다. 하지만 같은 수업을 듣는 학생인 이영수가 기본 웹 어플리케이션을 오픈 소스로 공개하고 과제 방향을 명확하게 집어주어 큰 도움을 받았다.  그리하여 어렵게 오픈 소스를 다뤄본 결과 오픈 소스를 사용하는 것의 중요성을 크게 느낄 수 있었다.  또 많은 사람들이 사용하는 오픈 소스가 왜 많이 사용 되는 지에 대하여 알아가는 것 또한 매우 유익한 과정이었다.
