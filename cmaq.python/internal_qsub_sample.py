            ## Need to define working_dir above this line
            ## Need to define jobid above this line
            ## example of modify the figdir= section above
            ##    jobid="aqm"+"_"+envir+"_"+date.strftime(YMD_date_format)+"_"+var[ivar]+"_"+cyc
            ##    figdir = figout+"/"+jobid
            task_cpu="02:00:00"
            plot_script=os.path.join(working_dir,jobid+".sh")
            print("Creating graphic script "+plot_script)
            if os.path.exists(plot_script):
                os.remove(plot_script)
            with open(plot_script, 'a') as sh:
                sh.write("#!/bin/bash -l\n")
                sh.write("#PBS -o "+log_dir+"/"+jobid+".log\n")
                sh.write("#PBS -e "+log_dir+"/"+jobid+".log\n")
                sh.write("#PBS -l place=shared,select=1:ncpus=1:mem=4500MB\n")
                sh.write("#PBS -N "+jobid+"\n")
                sh.write("#PBS -q dev_transfer\n")
                sh.write("#PBS -A AQM-DEV\n")
                sh.write("#PBS -l walltime="+task_cpu+"\n")
                sh.write("###PBS -l debug=true\n")
                sh.write("# \n")
                sh.write("export OMP_NUM_THREADS=1\n")
                sh.write("\n")
                sh.write("##\n")
                sh.write("##  Transfer "+jobid+" figures to RZDM\n")
                sh.write("##\n")
                sh.write("set -x\n")
                sh.write("\n")
                sh.write("   cd "+figdir+"\n")
                if 1 == 1 :
                    sh.write("   scp *  hchuang@rzdm:/home/www/emc/htdocs/mmb/hchuang/web/fig/"+date.strftime(Y_date_format)+"/"+date.strftime(YMD_date_format)+"/"+cyc+"\n")
                else:
                    sh.write("   scp *  hchuang@rzdm:/home/www/emc/htdocs/mmb/hchuang/transfer\n")
                sh.write("\n")
                sh.write("exit\n")
            print("submit "+plot_script)
            subprocess.call(["cat "+plot_script+" | qsub"], shell=True)
